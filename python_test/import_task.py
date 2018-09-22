import time, os
from celery import Celery

broker = 'redis://localhost:6379/'
backend = 'redis'
celery = Celery('test', broker=broker, backend=backend)
#os.environ['TASK_MODULE'] = 'import_task'

celery.conf.update(
    CELERY_RESULT_SERIALIZER='json'
)

@celery.task
def delayed_echo(msg):
    #print('Sleeping....')
    time.sleep(10)
   # print('Wake up....')
    return 'RECIEVED: '+msg
