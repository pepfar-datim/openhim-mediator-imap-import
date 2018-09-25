import os
import subprocess
import sys

from unittest import TestCase
from mock import patch
from celery import Celery
from python.import_manager import ENV_BROKER_URL, TaskService

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


class TaskServiceTest(TestCase):

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
        #We need to be able to run this with npm test or as a single Test in the IDE
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
        self.assertListEqual([], TaskService.get_all_tasks())

    def test_get_all_tasks_should_include_scheduled_tasks(self):
        ret = hello_world.apply_async(countdown=5)
        active_tasks = TaskService.get_all_tasks()
        self.assertEquals(1, active_tasks.__len__())
        #This effectively forces the test to end after the task has completed
        ret.get()


class ImportManagerTest(TestCase):

    @patch.object(TaskService, 'get_all_tasks')
    def test(self, get_all_tasks):
        print 'Running test'
        self.assertTrue(True)
        get_all_tasks.return_value = None
        self.assertIsNone(get_all_tasks())
