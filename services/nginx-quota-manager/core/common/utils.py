"""Common Functions"""

import datetime as dt
import time as tm


def data_not_found(data, api=None):
    """return 404 error with body"""
    api.abort(404, f"{data} not found")


def data_already_exist(data, api=None):
    """return 409 error with body"""
    api.abort(409, f"{data} already exist")


def utc_time(ms):
    """return UTC format time"""
    return dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=ms*100)


def str_time(ltime):
    """return string format time.

    The length of miliseconds is vary like '123.45678' or '123.456789'. So this
    function generates string format time which is aligned with 6 bytes as the
    following example of 'API Request Time':
    +-----+------------------------+--------------------+---------------+
    |     |    Quota Remainings    |                    |    Result     |
    | No. +--------+-------+-------+  API Request Time  +-------+-------+
    |     | Global | User1 | User2 |                    | User1 | User2 |
    +-----+--------+-------+-------+--------------------+-------+-------+
    | 001 |    5   |    4  |    3  | 16414365986.80042  |  True |  True |
    | 002 |    5   |    3  |    2  | 16414365986.801842 |  True |  True |
    | 003 |    5   |    2  |    1  | 16414365986.802189 |  True |  True |
    | 004 |    5   |    1  |    0  | 16414365986.80253  |  True | False |
    |     | user-2 quota exhausted | request-004 is denied.             |
    +-----+--------+-------+-------+--------------------+-------+-------+
    """
    ss, ms = f"{ltime}".split(".")
    return f"{ss}.{ms:6}"


class FakeClock(object):
    """A fake clock for testing.

    The concept of a fake clock can run faster than the system clock so that we
    can quickly test the rate limiter without waiting full second when using a
    function of sleep() function.

    Attributes:
        factor: A float value indicating how to scale down system sleep time.
                Regardless of scaling down a sleeping time, the time() returns
                real current time based on the formula of 'time() * _factor'.
                +--------+---------------------------+
                | factor |       sleep() second      |
                |        +--------------+------------+
                |        | system clock | fake clock |
                +--------+--------------+------------+
                |   1.0  |     1.000    |    1.000   |
                +--------+--------------+------------+
                |  10.0  |     1.000    |    0.100   |
                +--------+--------------+------------+
    """

    def __init__(self, factor=1):
        self._factor = factor

    def time(self):
        return tm.time() * self._factor

    def stime(self):
        return str_time(self.time())

    def sleep(self, seconds):
        tm.sleep(seconds / self._factor)
