"""Business Logic for Quota Limit Configuration API with Key/Value Store"""

from botocore.exceptions import ClientError
from core.common.constants import QuotaLimitPer as Per
from http import HTTPStatus


class QuotaLimitConfig:
    """Business Logic for Quota Limit Config API"""

    def __init__(self, namespace=None, datastore=None):
        self.namespace = namespace
        self.datastore = datastore

    def res_body(self, key='group', quota_limit=5, quota_remaining=5):
        return {
            'bucket_name': str(key),
            'quota_limit': int(quota_limit),
            'limit_per': Per.SEC,
            'quota_remaining': int(quota_remaining)
        }

    def get(self, user_id='group'):
        try:
            res = self.datastore.get_bucket(user_id)
            body = self.res_body(
                user_id, res['quota_limit'], res['quota_remaining']
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {}, 404
        else:
            return body, 200

    def put(self, data, user_id='group'):
        try:
            self.datastore.create_bucket(user_id, data)
            res = self.datastore.get_bucket(user_id)
            print(res)
            body = self.res_body(
                user_id, res['quota_limit'], res['quota_remaining']
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {}, 500
        else:
            return body, 200

    def delete(self, user_id='group'):
        try:
            self.datastore.delete_bucket(user_id)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {}, 404
        return {}, HTTPStatus.NO_CONTENT
