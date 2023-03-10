"""Business Logic for Rate Limit Request API"""

from core.common.constants import RateLimitLevel as Level, RateLimitPer as Per
from core.common.utils import data_not_found


class RateLimitDecrement:
    """Business Logic for Rate Limit Decrement API"""

    def __init__(self, limiter=None, namespace=None):
        self.limiter = limiter
        self.namespace = namespace

    def get(self, user_id=None):
        key = self._validate_limiter(user_id)
        if key is not None:
            code = 200 if self.limiter.process_request(key) else 429
            remaining = self.limiter.quota_remaining(key)
            return {
                'bucket_name': str(key),
                'quota_limit': self.limiter.quota_limit(key),
                'limit_per': Per.SEC,
                'quota_remaining': remaining
            }, code

    def _validate_limiter(self, user_id=None):
        key = Level.GLOBAL if user_id is None else user_id
        if not self.limiter.is_configured(key):
            data_not_found(key, self.namespace)
            return None
        return key
