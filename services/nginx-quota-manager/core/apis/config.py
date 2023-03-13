"""Business Logic for Rate Limit Policy Configuration API in Data Plane"""

from copy import deepcopy
from core.common.constants import (
    RateLimitLevel as Level,
    RateLimitPer as Per
)
from core.common.utils import data_not_found
from http import HTTPStatus


class RateLimitConfig:
    """Business Logic for Rate Limit Config API"""

    def __init__(self, limiter=None, namespace=None):
        self.limiter = limiter
        self.namespace = namespace

    def get(self, user_id=None):
        key = self._validate_limiter(user_id)
        if key is not None:
            return {
                'bucket_name': str(key),
                'quota_limit': self.limiter.quota_limit(key),
                'limit_per': Per.SEC,
                'quota_remaining': self.limiter.cur_remaining(key)
            }, HTTPStatus.OK

    def put(self, data, user_id=None):
        key = Level.GLOBAL if user_id is None else user_id
        code = 200 if self.limiter.is_configured(key) else 201
        return self._upsert(key, data), code

    def _upsert(self, key, data):
        quota_limit = data['quota_limit']
        if key == Level.GLOBAL:
            self.limiter.configure_global_limit(rps=quota_limit)
        else:
            self.limiter.configure_limit(user_id=key, rps=quota_limit)

        res = deepcopy(data)
        res['bucket_name'] = key
        res['quota_remaining'] = self.limiter.cur_remaining(key)
        return res

    def delete(self, user_id=None):
        key = self._validate_limiter(user_id)
        if key is not None:
            self.limiter.remove_bucket(key)
            return {}, HTTPStatus.NO_CONTENT

    def _validate_limiter(self, user_id=None):
        key = Level.GLOBAL if user_id is None else user_id
        if not self.limiter.is_configured(key):
            data_not_found(key, self.namespace)
            return None
        return key
