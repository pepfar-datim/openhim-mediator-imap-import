import os
import time
import logging
from celery import Celery

celery = Celery('tasks')
celery.config_from_object('celeryconfig')

@celery.task
def process_import(csv, country_code, period):
    logging.info('Executing cvs import task...')
    return 'Country code: '+country_code+ ' period: '+period
