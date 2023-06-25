import os
from typing import List
from minio import Minio
from app.core.config import settings

minioClient = Minio(settings.MINIO_HOST + ':' + str(settings.MINIO_PORT),
                    access_key=settings.MINIO_ROOT_USER,
                    secret_key=settings.MINIO_ROOT_PASSWORD,
                    secure=False)


class MinioClient:

    def __init__(self) -> None:
        print('init')
        print(settings.MINIO_HOST + ':' + str(settings.MINIO_PORT),
              settings.MINIO_ROOT_USER,
              settings.MINIO_ROOT_PASSWORD, settings.USER_ROOT_FOLDER)
        self.client = Minio(settings.MINIO_HOST + ':' + str(settings.MINIO_PORT),
                            access_key=settings.MINIO_ROOT_USER,
                            secret_key=settings.MINIO_ROOT_PASSWORD,
                            secure=False)

    def load_external_data(self,
                           dest_folder: str,
                           bucket: str = settings.USER_ROOT_FOLDER) -> str:

        dest_folder = str(dest_folder)
        print(f'dest_folder {dest_folder}')
        print(bucket)
        for file in self.client.list_objects(bucket, recursive=True, prefix=dest_folder):
            print('starting', file.object_name)
            self.client.fget_object(bucket, file.object_name, os.path.join(
                "/tmp", file.object_name))
        return os.path.join('/tmp', dest_folder)
