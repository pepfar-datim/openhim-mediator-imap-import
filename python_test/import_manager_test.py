import os
import subprocess
import sys

from unittest import TestCase
from mock import patch
from celery import Celery
from python.import_manager import TaskService
from python_test.import_task import hello_world, ENV_BROKER_URL, BROKER_PORT


def setUpModule():
    print '\nRunning tests for Python scripts'
    print '======================================================================'


def tearDownModule():
    print '\nEnd tests for Python scripts'
    print '======================================================================'


class TaskServiceTest(TestCase):

    redis_process = None
    worker_process = None
    """ TODO search for an available port instead """
    celery = Celery('testing', broker=os.getenv(ENV_BROKER_URL))

    @classmethod
    def setUpClass(cls):
        print('Starting redis server ')
        cmd = ['redis-server', '--port '+BROKER_PORT]
        cls.redis_process = subprocess.Popen(cmd)
        print 'Redis server pid: ' + cls.redis_process.pid.__str__()+'\n'
        cls.start_worker()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.shutdown_worker()
        finally:
            print '\nStopping redis server'
            cls.redis_process.terminate()

    @classmethod
    def start_worker(cls):
        print('Starting celery worker...')
        cmd = 'celery worker -A python_test.import_task -l info -b ' + os.getenv(ENV_BROKER_URL).__str__() + ' -n test'
        wrk_proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
        cls.worker_process = wrk_proc
        print 'Celery worker pid: ' + wrk_proc.pid.__str__()

        """ Wait until the worker is ready """
        while True:
            out = wrk_proc.stderr.readline()
            if (out == '' and wrk_proc.poll() is not None) or out.endswith('ready.\n'):
                if out.endswith('ready.\n'):
                    sys.stdout.write(out)
                    sys.stdout.flush()

                print 'Worker started successfully\n'
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

    @classmethod
    def shutdown_worker(cls):
        print '\nStopping celery worker'
        cls.worker_process.terminate()


    """ ===================== Actual TaskService Tests ===================== """

    #def test_get_active_tasks_should_return_nothing_if_no_active_tasks(self):
    #    self.assertListEqual([], TaskService.get_all_tasks())

    def test_get_all_tasks_should_return_all_active_tasks(self):
        ret = hello_world.apply_async(countdown=2)
        print 'Task Id: '+ret.task_id
        active_tasks = TaskService.get_all_tasks()
        self.assertEquals(1, active_tasks.__len__())


class ImportManagerTest(TestCase):

    @patch.object(TaskService, 'get_all_tasks')
    def test(self, get_all_tasks):
        print 'Running test'
        self.assertTrue(True)
        get_all_tasks.return_value = None
        self.assertIsNone(get_all_tasks())
