"""
This manager is responsible for mediating the import process of a csv file by ensuring that if a
given country submits an import, it gets blocked from making subsequent submissions until the
current import is complete.

It's also responsible for responding to the status requests of a country's import by a specified
task id. If the import is complete, it should include the results in the response in case of a success
otherwise error details in case of a failure.
"""

import os
import sys

from celery import Celery, Task

ENV_BROKER_URL = 'broker_url'
TASK_ID_KEY = 'id'
TASK_ID_SEPARATOR = '-'


# TODO Use an enum for exit codes, client code should interprete 0 as normal termination
"""
0, 1, 2 are reserved based on conventions where 0 is success, 1 errors in the script, 2 worng command usage
"""
ERROR_IMPORT_IN_PROGRESS = 3
ERROR_INVALID = 4


class ImportTask(Task):

    def run(self, csv, country_code, period):
        print 'Running task'


def get_celery():
    broker_url = os.getenv(ENV_BROKER_URL)
    return Celery('tasks', broker=broker_url, backend=ENV_BROKER_URL)


def import_csv(csv, country_code, period):
    """ Imports a csv file asynchronously, will ony process the import if the country has no
     existing import

        Arguments:
            csv (str): The csv file to import
            country_code (str): Country code of the country
            period (str): The period of the year the import is assigned to

        Returns:
              None
        """
    if has_existing_import(country_code):
        sys.exit(ERROR_IMPORT_IN_PROGRESS)

    return import_csv_async(csv, country_code, period)


def import_csv_async(csv, country_code, period):
    return Task().apply_async(task_id='my-id', args=[csv, country_code, period])


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