import logging

import redis
from django.conf import settings

lg = logging.getLogger(__name__)
r = redis.Redis(
    db=settings.RECOMMENDATION_SYSTEM['DB'],
    port=settings.RECOMMENDATION_SYSTEM['PORT'],
    host=settings.RECOMMENDATION_SYSTEM['HOST'],
)


class Recommender:
    @staticmethod
    def set_vlad():
        r.set('VLAD', 3)
        lg.debug(r.get('VLAD'))
