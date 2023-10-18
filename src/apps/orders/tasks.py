import logging

from celery import shared_task
from celery_singleton import Singleton

lg = logging.getLogger(__name__)


@shared_task
def log_message() -> str:
    lg.debug('Hello world')
    return 'God bless you'
