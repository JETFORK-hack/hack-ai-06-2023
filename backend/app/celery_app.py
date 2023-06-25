import os
from celery import Celery

# Настройка Celery
app = Celery(
    "worker",
    backend=os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    broker=os.environ.get(
        "CELERY_BROKER_URL", "redis://redis:6379/0"),
)

# Загрузка файла и обновление базы данных
# @app.task
# def parse_file(file_id: int):
#     print('it works! File id: ', file_id)
#     # Загрузите файл из Minio
#     # Обработайте файл с помощью parse_file
#     # Обновите запись в базе данных
#     pass

app.autodiscover_tasks(['app.api.upload'])
