"""Unit Test for Each Function of Rate Limiter Bucket"""

import time
from unittest import TestCase as t

from core.common.constants import DEFAULT_TIME_WINDOW, DEFAULT_RPS
from core.common.utils import FakeClock
from core.controller.rate_limiter import RateLimitBucket


def test_clear_and_quota_limit_remaining():
    # set up a bucket for testing clear(), quota_limit() and quota_remaining().
    bucket = RateLimitBucket(DEFAULT_RPS, DEFAULT_TIME_WINDOW)
    bucket.clear()

    # test the functions to check the variables are set.
    assert bucket.quota_remaining() == DEFAULT_RPS
    assert bucket._last_update_time <= time.time()


def test_decrement_cur_remaining():
    # set up a bucket for testing decrement() and cur_remaining().
    clock = FakeClock(10)
    bucket = RateLimitBucket(DEFAULT_RPS, DEFAULT_TIME_WINDOW, clock)

    # test the functions to check the variables are set.
    for quota_remaining in range(DEFAULT_RPS-1, -1, -1):
        t().assertTrue(bucket.decrement())
        assert bucket.quota_remaining() == quota_remaining
        assert bucket.cur_remaining() == quota_remaining
    clock.sleep(1)
    assert bucket.cur_remaining() == DEFAULT_RPS


def test_time_allowance():
    # set up a bucket for testing time_allowance().
    clock = FakeClock(10)
    bucket = RateLimitBucket(DEFAULT_RPS, DEFAULT_TIME_WINDOW, clock)

    # test the function to check the updated time allowance.
    for sec in range(5):
        res = bucket.time_allowance()
        assert res == sec
        clock.sleep(1)

    # test if time_allowance(sec) is recalculated after a new process request.
    bucket.decrement()
    res = bucket.time_allowance()
    assert res == 0
