"""Unit Test for Each Function of Rate Limiter"""

import pytest
from unittest import TestCase as t

from core.common.constants import RateLimitLevel as Level
from core.common.exceptions import RateLimitConfigNotFound
from core.controller.rate_limiter import RateLimiter
from core.common.constants import DEFAULT_USER_ID, DEFAULT_RPS
from core.common.utils import FakeClock


def test_configure_global_limit():
    # set up rate-limiter for testing configure_global_limit()
    limiter = RateLimiter()
    limiter.configure_global_limit(rps=DEFAULT_RPS)

    # test global rate-limiter to check if it is configured.
    t().assertTrue(limiter.is_configured())
    t().assertTrue(limiter.is_configured(Level.GLOBAL))
    assert limiter.quota_remaining() == DEFAULT_RPS
    assert limiter.quota_remaining(Level.GLOBAL) == DEFAULT_RPS


def test_configure_limit():
    # set up rate-limiter for testing configure_limit()
    limiter = RateLimiter()
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    # test user-level rate-limiter to check if it is configured.
    t().assertFalse(limiter.is_configured())
    t().assertFalse(limiter.is_configured(Level.GLOBAL))
    t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))
    assert limiter.quota_remaining(DEFAULT_USER_ID) == DEFAULT_RPS
    with pytest.raises(RateLimitConfigNotFound):
        limiter.quota_remaining()
        limiter.quota_remaining(Level.GLOBAL)


def test_process_request():
    # set up rate-limiter for testing process_request()
    limiter = RateLimiter()

    # test global-level rate-limiter request
    limiter.configure_global_limit(rps=DEFAULT_RPS)
    _validate_global_process_request(limiter)
    with pytest.raises(RateLimitConfigNotFound):
        limiter.process_request(DEFAULT_USER_ID)

    # test user-level rate-limiter request
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    _validate_user_rate_limit_process_request(limiter)


def test_quota_limit():
    # set up rate-limiter for testing quota_remaining()
    limiter = RateLimiter()

    # test last quota remaining prior to configuring global/user limiter
    with pytest.raises(RateLimitConfigNotFound):
        limiter.quota_remaining()
    with pytest.raises(RateLimitConfigNotFound):
        limiter.quota_remaining(Level.GLOBAL)
    with pytest.raises(RateLimitConfigNotFound):
        limiter.quota_remaining(DEFAULT_USER_ID)

    # test last quota remaining after configuring global/user limiter
    limiter.configure_global_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    assert limiter.quota_remaining() == DEFAULT_RPS
    assert limiter.quota_remaining(Level.GLOBAL) == DEFAULT_RPS
    assert limiter.quota_remaining(DEFAULT_USER_ID) == DEFAULT_RPS

    # test last quota remaining after global rate-limit request
    quota_limit = _validate_global_process_request(limiter)
    assert limiter.quota_remaining() == quota_limit


def test_cur_remaining():
    # set up rate-limiter for testing cur_remaining()
    clock = FakeClock(10)
    limiter = RateLimiter(clock)

    # test current quota remaining before configuring global/user limiter
    with pytest.raises(RateLimitConfigNotFound):
        limiter.cur_remaining()
    with pytest.raises(RateLimitConfigNotFound):
        limiter.cur_remaining(Level.GLOBAL)
    with pytest.raises(RateLimitConfigNotFound):
        limiter.cur_remaining(DEFAULT_USER_ID)

    # test current quota remaining after configuring global/user limiter
    limiter.configure_global_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    assert limiter.cur_remaining() == DEFAULT_RPS
    assert limiter.cur_remaining(Level.GLOBAL) == DEFAULT_RPS
    assert limiter.cur_remaining(DEFAULT_USER_ID) == DEFAULT_RPS

    # test current quota remaining after global rate-limit request
    quota_remaining = _validate_global_process_request(limiter)
    assert limiter.cur_remaining() == quota_remaining
    clock.sleep(1)
    assert limiter.cur_remaining() == DEFAULT_RPS


def test_remove_bucket_and_is_configured():
    # set up rate-limiter for testing remove_bucket() and is_configured()
    limiter = RateLimiter()

    # test removing bucket before configuring global/user limiter
    with pytest.raises(RateLimitConfigNotFound):
        limiter.remove_bucket()

    # test removing buckets after configuring global/user limiter
    limiter.configure_global_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    t().assertTrue(limiter.is_configured(Level.GLOBAL))
    t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))

    limiter.remove_bucket(Level.GLOBAL)
    limiter.remove_bucket(DEFAULT_USER_ID)

    t().assertFalse(limiter.is_configured(Level.GLOBAL))
    t().assertFalse(limiter.is_configured(DEFAULT_USER_ID))


def test_is_exhausted():
    # set up rate-limiter for testing is_exhausted()
    limiter = RateLimiter()

    # test is_exhausted() before configuring global/user limiter
    with pytest.raises(RateLimitConfigNotFound):
        limiter.is_exhausted()

    # test is_exhausted() buckets after configuring global/user limiter
    limiter.configure_global_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    for _ in range(DEFAULT_RPS):
        t().assertTrue(limiter.is_configured(Level.GLOBAL))
        t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))

        limiter.process_request(Level.GLOBAL)
        limiter.process_request(DEFAULT_USER_ID)


def _validate_global_process_request(limiter):
    """Validate global level rate-limiter process request"""
    quota_remaining = DEFAULT_RPS

    t().assertTrue(limiter.process_request())

    quota_remaining -= 1
    assert limiter.quota_remaining() == quota_remaining

    t().assertTrue(limiter.process_request(Level.GLOBAL))
    quota_remaining -= 1

    assert limiter.quota_remaining() == quota_remaining
    return quota_remaining


def _validate_user_rate_limit_process_request(limiter):
    """Validate a user level rate-limiter process request"""
    for i in range(DEFAULT_RPS):
        t().assertTrue(limiter.process_request(DEFAULT_USER_ID))
    t().assertFalse(limiter.process_request(DEFAULT_USER_ID))
