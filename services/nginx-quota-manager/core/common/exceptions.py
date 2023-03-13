"""Common Exceptions"""

from http import HTTPStatus


class RateLimitException(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    description = 'Failed to complete the request, please try again'
    code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message=None, code=None, payload=None, orig=None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload
        self.orig = orig
        if code is not None:
            self.status_code = code

    def to_dict(self):
        try:
            proc_payload = dict(self.payload or ())
        except TypeError:
            proc_payload = self.payload

        return {
            'error': self.__class__.__name__,
            'description': self.description,
            'message': self.message,
            'payload': proc_payload,
        }

    def __str__(self):
        return '(message=%s, payload=%s)' % (self.message, self.payload)


class RateLimitConfigNotFound(RateLimitException):
    status_code = HTTPStatus.NOT_FOUND
    description = 'The rate-limit policy is not configured'
