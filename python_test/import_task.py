from celery import Celery

celery = Celery('test', broker='redis://localhost:6379/')

celery.conf.update(
    CELERY_RESULT_SERIALIZER='json'
)

@celery.task
def hello_world():
    return 'Hello World!'
