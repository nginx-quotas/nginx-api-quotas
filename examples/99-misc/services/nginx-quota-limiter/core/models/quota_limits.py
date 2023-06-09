"""API Models for Quota Limit API in Data Plane"""

from core.common.constants import (
    QuotaLimitLevel as Level,
    QuotaLimitPer as Per,
    DEFAULT_RPS
)
from flask_restx import fields


def req_api_model():
    """Request API Model for Global/User Level Quota Limiter"""
    return {
        'quota_limit': fields.Integer(
            required=True,
            default=DEFAULT_RPS,
            description='the number of times you can request per second (rps)'
        ),
        'limit_per': fields.String(
            required=True,
            default=Per.SEC,
            description='requests per period of time such as second'
        )
    }


def res_api_model():
    """Response API Model for Global/User Level Quota Limiter"""
    res = req_api_model()
    res['bucket_name'] = fields.String(
        required=True,
        default=Level.GROUP,
        description='quota-limiter bucket key: e.g. user-id'
    )
    res['quota_remaining'] = fields.Integer(
        default=DEFAULT_RPS,
        description='remaining quota-units'
    )
    return res
