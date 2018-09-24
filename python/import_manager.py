import os
from celery import Celery

ENV_BROKER_URL = 'broker_url'


class TaskService:

    celery = None

    @classmethod
    def get_celery(cls):
        if cls.celery is None:
            cls.celery = Celery('tasks', broker=os.getenv(ENV_BROKER_URL))
        return cls.celery

    @classmethod
    def get_all_tasks(cls):
        celery = cls.get_celery()
        all_tasks = []
        inspect = celery.control.inspect()
        for tasks1 in inspect.reserved().values():
            all_tasks.extend(tasks1)
        for tasks2 in inspect.scheduled().values():
            all_tasks.extend(tasks2)
        for tasks3 in inspect.active().values():
            all_tasks.extend(tasks3)

        unique_tasks = []
        found_task_ids = []
        for task in all_tasks:
            task_id = task.get('id')
            if task_id not in found_task_ids:
                found_task_ids.append(task_id)
                unique_tasks.append(task)

        return unique_tasks

    @classmethod
    def get_task_by_id(cls, id):
        return None
