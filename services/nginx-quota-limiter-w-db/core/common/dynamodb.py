import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import time
from python_dynamodb_lock.python_dynamodb_lock import (
    DynamoDBLockClient
)


DYNAMO_URL = 'http://host.docker.internal:8000'
ACCESS_KEY = 'fakeMyKeyId'
SECRET_KEY = 'fakeSecretAccessKey'
AWS_REGION = 'us-west-1'
BUCKET_TBL = 'quota_remaining'


class QuotaLimitDynamoDB:
    def __init__(self):
        self.db_service = self.get_service_resource()
        self.lock_client = DynamoDBLockClient(
            self.db_service, BUCKET_TBL
        )

    def __del__(self):
        self.lock_client.close()

    def get_service_resource(self):
        return boto3.resource('dynamodb',
                              aws_access_key_id=ACCESS_KEY,
                              aws_secret_access_key=SECRET_KEY,
                              region_name=AWS_REGION,
                              endpoint_url=DYNAMO_URL)

    def get_credentials(self):
        session = boto3.Session()
        credentials = session.get_credentials()
        credentials = credentials.get_frozen_credentials()
        return credentials.access_key, credentials.secret_key

    def acquire_lock(self, key):
        return self.lock_client.acquire_lock(key)

    def release_lock(self, lock):
        return lock.release()

    def create_table(self):
        try:
            table = self.db_service.create_table(
                TableName=BUCKET_TBL,
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 3,
                    'WriteCapacityUnits': 3
                }
            )
            table.wait_until_exists()
            print(f" + created {table.item_count} table of {BUCKET_TBL}.")

        except Exception as e:
            if e.__class__.__name__ == 'ResourceInUseException':
                print(f" + tried to create a {BUCKET_TBL} table:" +
                      " but it already exists.")
            else:
                raise e

    def create_bucket(self, bucket_key, data=dict()):
        try:
            quota_limit = data.get('quota_limit', 5)
            quota_remaining = data.get('quota_remaining', quota_limit)
            table = self.db_service.Table(BUCKET_TBL)
            response = table.put_item(
                Item={
                    'user_id': bucket_key,
                    'quota_limit': Decimal(quota_limit),
                    'quota_remaining': Decimal(quota_remaining),
                    'limit_per': 'rps',
                    'last_update': Decimal(time.time())
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(f" + created a bucket of {bucket_key}.")
            print(f"   - response: {response}")

    def get_bucket(self, bucket_key):
        try:
            table = self.db_service.Table(BUCKET_TBL)
            response = table.get_item(
                Key={
                    'user_id': bucket_key
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(f" + get a bucket of {bucket_key}.")
            if 'Item' in response:
                print(f"   - response: {response['Item']}")
                return response['Item']
            print("   - response: not found")
            return {}

    def list_buckets(self):
        try:
            table = self.db_service.Table(BUCKET_TBL)
            response = table.scan()
            data = response['Items']
            while 'LastEvaluatedKey' in response:
                response = table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'])
                data.extend(response['Items'])

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(" + list all of buckets:")
            print(f"   - response: {data}")
            return data

    def update_bucket(self, bucket_key, data=dict()):
        try:
            quota_limit = data.get('quota_limit', 5)
            quota_remaining = data.get('quota_remaining', 5)
            last_update = data.get('last_update', time.time())
            table = self.db_service.Table(BUCKET_TBL)
            response = table.update_item(
                Key={
                    'user_id': bucket_key
                },
                UpdateExpression='set quota_limit=:l, ' +
                'quota_remaining=:r, limit_per=:p, last_update=:u',
                ExpressionAttributeValues={
                    ':l': Decimal(quota_limit),
                    ':r': Decimal(quota_remaining),
                    ':p': 'rps',
                    ':u': Decimal(last_update)
                },
                ReturnValues='UPDATED_NEW'
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(f" + updated a bucket of {bucket_key}.")
            print(f"   - response: {response}")
            return response

    def delete_bucket(self, bucket_key):
        try:
            table = self.db_service.Table(BUCKET_TBL)
            response = table.delete_item(
                Key={
                    'user_id': bucket_key
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == \
                    "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            print(f" + deleted a bucket of {bucket_key}.")
            print(f"   - response: {response}")
            return response
