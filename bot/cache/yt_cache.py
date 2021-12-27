import hashlib

from cachetools import TTLCache
from datetime import datetime, timedelta

class YTCache(TTLCache):

    def __init__(self):
        DEFAULT_MAX_SIZE=100
        DEFAULT_TTL = timedelta(hours=12)
        super().__init__(DEFAULT_MAX_SIZE, DEFAULT_TTL, timer=datetime.now)

    @staticmethod
    def hash(key):
        return hashlib.sha1(key.encode('UTF-8')).hexdigest()
