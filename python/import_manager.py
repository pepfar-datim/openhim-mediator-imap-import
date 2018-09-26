import os
from celery import Celery

ENV_BROKER_URL = 'broker_url'
TASK_ID_KEY = 'id'
TASK_ID_SEPARATOR = '-'


def get_celery():
    broker_url = os.getenv(ENV_BROKER_URL)
    return Celery('tasks', broker=broker_url, backend=ENV_BROKER_URL)


def has_existing_import(country_code):
    """ Checks if the country has an existing import request that is not completed, this will
    typically return true even if the import task is still queued up and waiting for execution

    Arguments: the country code to check against

    Returns:
          const:`True` if the country has an existing import request otherwise const:`False`
    """

    country_task = None
    for task in get_all_tasks():
        if task.get(TASK_ID_KEY).startswith(country_code):
            country_task = task
            break

    return country_task is not None


def get_all_tasks():
    celery = get_celery()
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
        task_id = task.get(TASK_ID_KEY)
        if task_id not in found_task_ids:
            found_task_ids.append(task_id)
            unique_tasks.append(task)

    return unique_tasks


def get_task_status(task_id):
    return get_celery().control.inspect().query_task(task_id)