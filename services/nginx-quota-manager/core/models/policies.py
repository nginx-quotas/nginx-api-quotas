"""API Models for Rate Limit Policy API in Control Plane"""

from flask_restx import fields


def req_api_model():
    """Request API Model for Rate Limit Policies"""
    return {
        'name': fields.String(required=True,
                              description='rate-limit policy name'),
        'level': fields.String(description='global or user'),
        'rate': fields.String(description='r/s: requests per second'),
        'req_cnt': fields.Integer(description='numer of request per period')
    }


def res_api_model():
    """Response API Model for Rate Limit Policies"""
    res = req_api_model()
    res['id'] = fields.Integer(required=True,
                               description='rate-limit policy ID')
    return res
