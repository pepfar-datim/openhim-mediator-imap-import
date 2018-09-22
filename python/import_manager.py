import os
from celery import Celery

broker = 'redis://localhost:6379/'
#backend = 'redis'
#module = os.getenv('TASK_MODULE', 'import_task')
celery = Celery('tasks', broker=broker)


class TaskService:

    def get_active_tasks(self):
        #print celery
        return []

    def get_task_by_id(self, id):
        return None
