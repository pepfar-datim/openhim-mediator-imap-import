import os
import sys
import time
import subprocess

from unittest import TestCase
from mock import patch
from celery import Celery
from python import import_manager
from python.import_manager import ENV_BROKER_URL, TASK_ID_KEY, TASK_ID_SEPARATOR, ERROR_IMPORT_IN_PROGRESS

dir_path = os.path.dirname(os.path.realpath(__file__))
redis_base_dir = dir_path+'/redis'
print redis_base_dir
redis_port = '6381'
broker_url = 'redis://localhost:'+redis_port+'/'
os.environ[ENV_BROKER_URL] = broker_url
celery = Celery('import_manager_test', broker=broker_url, backend=broker_url)

def setUpModule():
    print '\nRunning tests for Python scripts'
    print '======================================================================'


def tearDownModule():
    print '\nEnd tests for Python scripts'
    print '======================================================================'


@celery.task
def hello_world():
    return 'Hello World!'

@celery.task
def wait_task(duration):
    print 'Running for '+duration.__str__()+'s'
    time.sleep(duration)


class TaskTest(TestCase):

    redis_process = None
    hostname = 'test'
    worker_ready = 'celery@'+hostname+' ready.\n'

    @classmethod
    def setUpClass(cls):
        cls.start_redis_server()
        cls.start_worker()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.shutdown_worker()
        finally:
            cls.stop_redis_server()

    @classmethod
    def start_redis_server(cls):
        print('Starting redis server ...')
        cmd = [redis_base_dir + '/bin/redis-server', redis_base_dir + '/redis.conf']
        cls.redis_process = subprocess.Popen(cmd)
        print 'Redis server pid: ' + cls.redis_process.pid.__str__() + '\n'

    @classmethod
    def stop_redis_server(cls):
        print '\nShutting down redis server'
        cls.redis_process.terminate()

    @classmethod
    def start_worker(cls):
        print('Starting celery worker...')
        # We need to be able to run this with npm test or as a single Test in the IDE
        module = '.import_manager_test'
        package = 'python_test'
        if os.getcwd().__contains__(package) is False:
            module = package+module
        cmd = 'celery worker -A '+module+' -l info -b ' + broker_url + ' -n '+cls.hostname
        worker_process = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
        print 'Celery worker pid: ' + worker_process.pid.__str__()

        """ Wait until the worker is ready """
        while True:
            out = worker_process.stderr.readline()
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

            if out.endswith(cls.worker_ready):
                print 'Worker started successfully\n'
                break

    @classmethod
    def shutdown_worker(cls):
        print '\nStopping celery worker'
        celery.control.broadcast('shutdown')

    """ ===================== Actual TaskService Tests ===================== """

    def test_get_active_tasks_should_return_nothing_if_no_active_tasks(self):
        self.assertListEqual([], import_manager.get_all_tasks())

    def test_get_all_tasks_should_include_active_tasks(self):
        task_id = 'ug'
        result = wait_task.apply_async(task_id=task_id, args=[5])
        tasks = import_manager.get_all_tasks()
        # This ensures the worker thread isn't still running when the test ends
        result.get()
        self.assertEquals(1, len(tasks))
        task = tasks[0]
        self.assertEquals(task_id, task.get(TASK_ID_KEY))

    def test_get_all_tasks_should_include_scheduled_tasks(self):
        result = hello_world.apply_async(countdown=5)
        tasks = import_manager.get_all_tasks()
        result.get()
        self.assertEquals(1, len(tasks))
        task = tasks[0]
        self.assertEquals(result.id, task.get('request').get(TASK_ID_KEY))
        self.assertIsNotNone(task.get('eta'))

    # TODO include tests that ensures reserved (recieved and not scheduled but waiting for execution)


class ImportManagerTest(TestCase):

    @patch('python.import_manager.get_all_tasks')
    def test_has_existing_import_should_return_false_if_there_no_import_task_for_the_country(self, get_all_tasks):
        get_all_tasks.return_value = [{TASK_ID_KEY: 'KE'+TASK_ID_SEPARATOR+'some-uuid'}]
        self.assertFalse(import_manager.has_existing_import('UG'))

    @patch('python.import_manager.get_all_tasks')
    def test_has_existing_import_should_return_True_if_there_an_import_task_for_the_country(self, get_all_tasks):
        country_code = 'UG'
        get_all_tasks.return_value = [{TASK_ID_KEY: country_code+TASK_ID_SEPARATOR+'some-uuid'}]
        self.assertTrue(import_manager.has_existing_import(country_code))

    @patch('python.import_manager.has_existing_import')
    def test_import_csv_should_fail_if_the_country_has_an_import_in_progress(self, has_existing_import):
        country_code = 'UG'
        has_existing_import.return_value = True
        with self.assertRaises(SystemExit) as cm:
            import_manager.import_csv('some_file.csv', country_code, 'some-period')
        self.assertEquals(ERROR_IMPORT_IN_PROGRESS, cm.exception.code)
