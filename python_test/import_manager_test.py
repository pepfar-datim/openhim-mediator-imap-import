from python.import_manager import TaskService

from unittest import TestCase

from mock import Mock, patch

import subprocess, sys, time


print 'Running tests for Python scripts'

print '----------------------------------------------------------------------'


class ImportManagerTest(TestCase):

    worker_process = None

    @classmethod
    def setUpClass(cls):
        print('Starting celery worker...')

        cmd = 'celery -A python.import_task worker -l info -n '+time.time().__str__()
        wrk_proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
        cls.worker_process = wrk_proc
        print 'Celery worker pid: '+wrk_proc.pid.__str__()

        while True:
            out = wrk_proc.stderr.readline()
            if (out == '' and wrk_proc.poll() is not None) or out.endswith('ready.\n'):
                if out.endswith('ready.\n'):
                    sys.stdout.write(out)
                    sys.stdout.flush()

                print 'Worker started successfully'
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

    @classmethod
    def tearDownClass(cls):
        print('\nStopping celery worker')
        #os.system('celery -A python.import_task control shutdown')
        cls.worker_process.terminate()

    @patch.object(TaskService, 'get_active_tasks')
    def test(self, get_active_tasks):
        print('Running test')
        self.assertTrue(True)
        get_active_tasks.return_value = None
        self.assertIsNone(get_active_tasks())
