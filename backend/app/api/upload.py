import os
import io

from app.celery_app import app as celery_app
from app.models.files import File
from app.deps.minio import MinioClient
from app.deps.model.get_text_from_pdf import parse_pdf_bucket
from app.models.remark import Remark
from app.deps.model.predict import predict
from app.schemas.remark import RemarkWithFileName
from fastapi import HTTPException, Body
from sqlalchemy import create_engine, exc, select
from sqlalchemy.orm import sessionmaker

import uuid
from app.models.bundle import Bundle
from app.deps.db import get_async_session
from minio import Minio
from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.core.config import settings


router = APIRouter(prefix="/upload")
minioClient = Minio(settings.MINIO_HOST + ':' + str(settings.MINIO_PORT),
                    access_key=settings.MINIO_ROOT_USER,
                    secret_key=settings.MINIO_ROOT_PASSWORD,
                    secure=False)

found = minioClient.bucket_exists(settings.USER_ROOT_FOLDER)
if not found:
    minioClient.make_bucket(settings.USER_ROOT_FOLDER)

# соединение с БД для celery
engine = create_engine(settings.DATABASE_URL)
CeleryDb = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Загрузка файла и обновление базы данных
@celery_app.task(task_track_started=True, bind=True)
def parse_file(self, folder_id: str, goldanName: str) -> None:
    local_folder_path: str = MinioClient().load_external_data(folder_id)
    self.update_state(state='PROGRESS', meta={'done': 0, 'total': 100})
    documents = parse_pdf_bucket(local_folder_path, self.update_state)
    self.update_state(state='PROGRESS', meta={'done': 2, 'total': 4})
    df_remarks = predict(documents, goldanName)
    self.update_state(state='PROGRESS', meta={'done': 3, 'total': 4})
    print('folder_id')
    print(folder_id)
    print('df_remarks')
    print(df_remarks)

    session = None
    try:
        # тут можете использовать db для работы с вашей базой данных
        session = CeleryDb()
        print(type(df_remarks))
        if df_remarks is None or df_remarks.empty:
            bundle = session.get(Bundle, folder_id)
            bundle.status = 'ERROR'
            bundle.message = 'Не удалось обнаружить эталонную сущность в переданных данных'
            session.add(bundle)
            session.commit()
            raise Exception(
                'Не удалось обнаружить эталонную сущность в переданных данных')

        for name in df_remarks['doc_name'].unique():
            print(f'folder_id {folder_id}, name {name}')
            file = session.query(File).filter(
                File.download_id == folder_id, File.name == name).one()
            print(f'file.id {file.id}, folder_id {folder_id}, name {name}')

            for remark in df_remarks[df_remarks['doc_name'] == name].drop(
                    'doc_name', axis=1).to_dict('records'):
                print(f'file {file.id}, remark {remark}')
                file_obj = Remark(file_id=file.id, **remark)
                session.add(file_obj)
            session.commit()
        bundle = session.get(Bundle, folder_id)
        bundle.status = 'SUCCESS'
        session.add(bundle)
        session.commit()
    except Exception as e:
        session.commit()
        raise e
    finally:
        if session:
            session.close()


@router.post('/files')
async def upload_file(
    files: list[UploadFile],
    goldanName: str = Body(default='', title="Эталонное значение"),
    session: AsyncSession = Depends(get_async_session)
):
    # Проверка валидности входных данных
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    bundle = Bundle(id=uuid.uuid4())
    session.add(bundle)

    print('goldanName', goldanName)

    try:
        for file in files:
            # Проверка валидности файла
            if not file.filename:
                raise HTTPException(
                    status_code=400, detail=f"Invalid file: {file}")

            try:
                print(file)
                # minioClient.fput_object(
                #     settings.USER_ROOT_FOLDER, os.path.join(str(bundle.id), file.filename), file.file.fileno())
                file_content = await file.read()
                file_size = len(file_content)

                # Преобразуем содержимое файла в байтовый поток
                data = io.BytesIO(file_content)

                # Отправляем файл в Minio
                minioClient.put_object(
                    settings.USER_ROOT_FOLDER,
                    os.path.join(str(bundle.id), file.filename),
                    data,
                    file_size
                )

                file_obj = File(download=bundle, path=os.path.join(
                    str(bundle.id), file.filename), name=file.filename, size=file_size)
                session.add(file_obj)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # task = parse_file.delay(str(bundle.id))
        # Запрашиваем обработку задачи
        parse_file.apply_async(
            args=[str(bundle.id), goldanName], task_id=str(bundle.id))

        await session.commit()
    except exc.SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": 'ok', "id": str(bundle.id)}


@router.get('/result/{bulk_id}')
async def get_result(bulk_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        bundle = await session.execute(
            select(Bundle)
            .where(Bundle.id == bulk_id)
        )
        bundle = bundle.scalars().first()
        if not bundle:
            raise HTTPException(
                status_code=404, detail="Задача на проверку не найдена")
        print('bundle', bundle.status)
        # Проверяем статус задачи
        if bundle.status != 'SUCCESS':
            if bundle.status == 'FAILURE' or bundle.status == 'ERROR':
                return {"status": 'FAILURE', 'message': bundle.message}
            current_job = parse_file.AsyncResult(str(bundle.id))
            new_status = current_job.state
            if new_status and new_status != bundle.status:
                print('update status')
                bundle.status = new_status
                session.add(bundle)
                await session.commit()
            return {"status": bundle.status, 'info': bundle, 'detail': current_job.info}

        stmt = (
            select(File.name, Remark)
            .join(File, File.id == Remark.file_id)
            .filter(File.download_id == bulk_id)
            .order_by(File.name, Remark.page_num)
        )

        result = await session.execute(stmt)

        remarks_with_names = [
            RemarkWithFileName(
                id=remark.id,
                file_id=remark.file_id,
                file_name=file_name,
                page_num=remark.page_num,
                golden_name=remark.golden_name,
                targets=remark.targets,
                candidate=remark.candidate,
                probability=remark.probability,
                similarity=remark.similarity,
            )
            for file_name, remark in result.all()
        ]

        return {"status": bundle.status, "result": remarks_with_names}
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch('/remark/{remark_id}')
async def feedback(remark_id: int,
                   is_correct: bool | None = Body(embed=True,
                                                  default=None, title="Правильность результата"),
                   session: AsyncSession = Depends(get_async_session)):
    try:
        remark = await session.get(Remark, remark_id)
        if not remark:
            raise HTTPException(
                status_code=404, detail="Результат не найден")
        remark.is_correct = is_correct
        session.add(remark)
        await session.commit()
        return {"status": "ok", 'id': remark_id, 'is_correct': is_correct}
    except exc.SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
