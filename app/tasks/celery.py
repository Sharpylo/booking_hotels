from celery import Celery

from app.config import settings

celery = Celery(
    settings.CELERY_NAME,
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
    include=['app.tasks.tasks']
)