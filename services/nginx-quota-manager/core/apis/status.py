"""Business Logic for Rate Limiter Status API"""

from core.common.constants import RateLimitLevel as Level, RateLimitPer as Per
from core.common.utils import data_not_found
from http import HTTPStatus


class RateLimitStatus:
    """Business Logic for Rate Limit Status API"""

    def __init__(self, limiter=None, namespace=None):
        self.limiter = limiter
        self.namespace = namespace

    def list(self):
        res = [self._data(key) for key in self.limiter.buckets.keys()]
        return res, 200 if self.limiter.buckets else 404

    def get(self, user_id=None):
        key = self._validate_limiter(user_id)
        if key is not None:
            return self._data(key), HTTPStatus.OK

    def _data(self, key):
        return {
            'bucket_name': key,
            'quota_limit': self.limiter.quota_limit(key),
            'limit_per': Per.SEC,
            'quota_remaining': self.limiter.quota_limit(key)
        }

    def _validate_limiter(self, user_id=None):
        key = Level.GLOBAL if user_id is None else user_id
        if not self.limiter.is_configured(key):
            data_not_found(key, self.namespace)
            return None
        return key
