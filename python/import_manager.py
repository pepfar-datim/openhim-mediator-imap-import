"""
This manager is responsible for mediating the import process of a csv file by ensuring that if a
given country submits an import, it gets blocked from making subsequent submissions until the
current import is complete.

It's also responsible for responding to the status requests of a country's import by a specified
task id. If the import is complete, it should include the results in the response in case of a success
otherwise error details in case of a failure.

To run an import using this manager client code should call the method below,

import_csv(script_filename, csv, country_code, period)

"""

import os
import sys
import uuid
import subprocess

from celery import Celery

ENV_CELERY_CONFIG = 'celery_config'
ENV_BROKER_URL = 'broker_url'
ENC_IMPORT_SCRIPT_FILENAME = 'import_script_filename'

TASK_ID_KEY = 'id'
TASK_ID_SEPARATOR = '-'
# TODO Use an enum for exit codes, client code should interprete 0 as normal termination
"""
0, 1, 2 are reserved based on conventions where 0 is success, 
1 is errors in the script, 2 wrong command usage
"""
ERROR_IMPORT_IN_PROGRESS = 3
ERROR_INVALID = 4

celery = Celery('import_task')
celery.config_from_object(os.getenv(ENV_CELERY_CONFIG, 'python.celeryconfig'))

@celery.task
def import_task(script_filename, csv, country_code, period):
    # Calls the specified python import script with along with the rest of the args
    cmd = ['python', script_filename]
    return subprocess.check_output(cmd)

def get_celery():
    broker_url = os.getenv(ENV_BROKER_URL)
    return Celery('tasks', broker=broker_url, backend=broker_url)


def import_csv(script_filename, csv, country_code, period):
    """ Imports a csv file asynchronously, will ony process the import if the country has no
     existing import

        Arguments:
            script_filename (str): The name of the python import script
            csv (str): The csv file to import
            country_code (str): Country code of the country
            period (str): The period of the year the import is assigned to

        Returns:
              None
        """
    if has_existing_import(country_code):
        sys.exit(ERROR_IMPORT_IN_PROGRESS)

    return import_csv_async(script_filename, csv, country_code, period)


def import_csv_async(script_filename, csv, country_code, period):
    # Runs the import asynchronously
    task_id = country_code+TASK_ID_SEPARATOR+uuid.uuid4().__str__()
    import_task.apply_async(task_track_started=True, task_id=task_id, args=[script_filename, csv, country_code, period])
    return task_id


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


def get_task_results(task_id):
    return celery.AsyncResult(task_id)
