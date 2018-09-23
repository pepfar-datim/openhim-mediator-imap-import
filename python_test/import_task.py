import os
from celery import Celery

ENV_BROKER_URL = 'broker_url'
BROKER_PORT = '6381'
broker_url = 'redis://localhost:'+BROKER_PORT+'/'
os.environ[ENV_BROKER_URL] = broker_url
celery = Celery('tasks', broker=broker_url)

@celery.task
def hello_world():
    return 'Hello World!'
