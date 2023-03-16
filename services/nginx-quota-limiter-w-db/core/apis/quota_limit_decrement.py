"""Business Logic for Quota Limit Request API"""

from botocore.exceptions import ClientError
from core.common.constants import QuotaLimitPer as Per
import time


class QuotaLimitDecrement:
    """Business Logic for Quota Limit Decrement API"""

    def __init__(self, namespace=None, datastore=None):
        self.namespace = namespace
        self.datastore = datastore
        self._time_window = 1

    def get_body(
        self, key='group', quota_limit=5, quota_remaining=5, t=time.time()
    ):
        return {
            'bucket_name': str(key),
            'quota_limit': int(quota_limit),
            'limit_per': Per.SEC,
            'quota_remaining': int(quota_remaining),
            'last_update': float(t)
        }

    def time_allowance(self, last_update):
        """Return the number of seconds until the quota resets."""
        time_passed = time.time() - last_update
        return int(time_passed // self._time_window)

    def decrement(self, quota_limit, quota_remaining, last_update):
        """Reduce the quota remaining."""
        time_allowance = self.time_allowance(last_update)
        quota_remaining += time_allowance * quota_limit
        last_update += time_allowance * self._time_window

        if quota_remaining >= quota_limit:
            quota_remaining = quota_limit
            last_update = time.time()

        if quota_remaining < 1:
            return False, quota_remaining, last_update

        quota_remaining -= 1
        return True, quota_remaining, last_update

    def get(self, user_id='group'):
        try:
            cur_data = self.datastore.get_bucket(user_id)

            quota_limit = cur_data['quota_limit']
            quota_remaining = cur_data['quota_remaining']
            last_update = float(cur_data['last_update'])
            res, new_remaining, new_update = self.decrement(
                quota_limit, quota_remaining, last_update
            )

            body = self.get_body(
                user_id, quota_limit, new_remaining, new_update
            )
            self.datastore.update_bucket(user_id, body)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return self.get_body(user_id), 404
        except KeyError:
            return self.get_body(user_id), 404
        else:
            if not res:
                return body, 429
            return body, 200
