import os
import time
import logging
from celery import Celery

broker = 'redis://localhost:6379/'
backend = os.getenv('CELERY_BACKEND_URL', 'redis')
celery = Celery('import_tasks', broker=broker, backend=backend)

celery.conf.update(
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ENABLE_UTC=True
)

@celery.task
def echo(msg):
    #print('Sleeping....')
    #time.sleep(2)
    #print('Wake up....')
    return msg
