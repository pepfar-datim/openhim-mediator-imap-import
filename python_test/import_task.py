import os

from redislite import Redis
from celery import Celery

redis = Redis()
REDIS_SOCKET_PATH = 'redis+socket://'+redis.socket_file

ENV_BROKER_URL = 'broker_url'
os.environ[ENV_BROKER_URL] = REDIS_SOCKET_PATH
celery = Celery('test_tasks', broker=os.environ[ENV_BROKER_URL])

@celery.task
def hello_world():
    return 'Hello World!'
