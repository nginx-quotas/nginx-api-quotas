"""Common Constants"""


class Duration(object):
    SEC = 1
    MIN = 60
    HOUR = 3600
    DAY = 86400
    MON = 2592000


class QuotaLimitLevel(object):
    GROUP = 'group'
    USER = 'user'
    QUOTA = 'quota'


class QuotaLimitPer(object):
    SEC = 'rps'
    MIN = 'rpm'
    HOUR = 'rph'
    DAY = 'rpd'
    MON = 'rpM'


class QuotaLimitAlgorithm(object):
    TOKEN_BUCKET = 1
    SLIDING_WINDOW_COUNTER = 2


DEFAULT_RPS = 5
DEFAULT_USER_ID = 1
DEFAULT_TIME_WINDOW = 1
