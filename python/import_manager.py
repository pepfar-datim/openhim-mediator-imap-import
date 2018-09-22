from celery import Celery

broker = 'redis://localhost:6379/'
celery = Celery('tasks', broker=broker)


class TaskService:

    @staticmethod
    def get_all_tasks():
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

    @staticmethod
    def get_task_by_id(id):
        return None
