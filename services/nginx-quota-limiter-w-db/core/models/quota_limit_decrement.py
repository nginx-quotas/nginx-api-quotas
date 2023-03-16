"""API Models for Decrement API"""

from core.common.constants import (
    QuotaLimitLevel as Level,
    QuotaLimitPer as Per,
    DEFAULT_RPS
)
from flask_restx import fields
import time


def req_api_model():
    return {}


def res_api_model():
    """Response API Model for Group/User Level Quota Limiter"""
    res = {}
    res['bucket_name'] = fields.String(
        required=True,
        default=Level.GROUP,
        description='quota-limiter bucket key: e.g. user-id'
    )
    res['quota_limit'] = fields.Integer(
        default=DEFAULT_RPS,
        description='the number of times you can request per second (rps)'
    )
    res['quota_remaining'] = fields.Integer(
        default=DEFAULT_RPS,
        description='quota remainining'
    )
    res['limit_per'] = fields.String(
        default=Per.SEC,
        description='requests per period of time such as second'
    )
    res['last_update'] = fields.Float(
        default=time.time(),
        description='last update time'
    )
    return res
