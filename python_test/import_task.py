from __future__ import absolute_import, unicode_literals

import logging
from celery import Celery


from .import_manager_test import celery

#celery = Celery('import_task')
#celery.config_from_object('celeryconfig')

@celery.task
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    #celery.start()
    print 'HERE'

