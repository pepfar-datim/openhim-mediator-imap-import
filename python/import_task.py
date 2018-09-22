import os
import time
import logging
from celery import Celery

broker = 'redis://localhost:6379/'
backend = os.getenv('CELERY_BACKEND_URL', 'redis')
celery = Celery('import_task', broker=broker, backend=backend)

celery.conf.update(
    CELERY_RESULT_SERIALIZER='json'
)

@celery.task
def echo(msg):
    print('Sleeping....')
    time.sleep(10)
    print('Wake up....')
    return 'cool: '+msg
