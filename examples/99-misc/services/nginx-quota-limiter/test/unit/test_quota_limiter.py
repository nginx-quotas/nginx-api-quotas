"""Unit Test for Each Function of Quota Limiter"""

import pytest
from unittest import TestCase as t

from core.common.constants import QuotaLimitLevel as Level
from core.common.exceptions import QuotaLimitConfigNotFound
from core.controller.quota_limiter import QuotaLimiter
from core.common.constants import DEFAULT_USER_ID, DEFAULT_RPS
from core.common.utils import FakeClock


def test_configure_group_limit():
    # set up quota-limiter for testing configure_group_limit()
    limiter = QuotaLimiter()
    limiter.configure_group_limit(rps=DEFAULT_RPS)

    # test group quota-limiter to check if it is configured.
    t().assertTrue(limiter.is_configured())
    t().assertTrue(limiter.is_configured(Level.GROUP))
    assert limiter.quota_remaining() == DEFAULT_RPS
    assert limiter.quota_remaining(Level.GROUP) == DEFAULT_RPS


def test_configure_limit():
    # set up quota-limiter for testing configure_limit()
    limiter = QuotaLimiter()
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    # test user-level quota-limiter to check if it is configured.
    t().assertFalse(limiter.is_configured())
    t().assertFalse(limiter.is_configured(Level.GROUP))
    t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))
    assert limiter.quota_remaining(DEFAULT_USER_ID) == DEFAULT_RPS
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.quota_remaining()
        limiter.quota_remaining(Level.GROUP)


def test_process_request():
    # set up quota-limiter for testing process_request()
    limiter = QuotaLimiter()

    # test group-level quota-limiter request
    limiter.configure_group_limit(rps=DEFAULT_RPS)
    _validate_group_process_request(limiter)
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.process_request(DEFAULT_USER_ID)

    # test user-level quota-limiter request
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    _validate_user_quota_limit_process_request(limiter)


def test_quota_limit():
    # set up quota-limiter for testing quota_remaining()
    limiter = QuotaLimiter()

    # test last quota remaining prior to configuring group/user limiter
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.quota_remaining()
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.quota_remaining(Level.GROUP)
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.quota_remaining(DEFAULT_USER_ID)

    # test last quota remaining after configuring group/user limiter
    limiter.configure_group_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    assert limiter.quota_remaining() == DEFAULT_RPS
    assert limiter.quota_remaining(Level.GROUP) == DEFAULT_RPS
    assert limiter.quota_remaining(DEFAULT_USER_ID) == DEFAULT_RPS

    # test last quota remaining after group quota-limit request
    quota_limit = _validate_group_process_request(limiter)
    assert limiter.quota_remaining() == quota_limit


def test_cur_remaining():
    # set up quota-limiter for testing cur_remaining()
    clock = FakeClock(10)
    limiter = QuotaLimiter(clock)

    # test current quota remaining before configuring group/user limiter
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.cur_remaining()
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.cur_remaining(Level.GROUP)
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.cur_remaining(DEFAULT_USER_ID)

    # test current quota remaining after configuring group/user limiter
    limiter.configure_group_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)
    assert limiter.cur_remaining() == DEFAULT_RPS
    assert limiter.cur_remaining(Level.GROUP) == DEFAULT_RPS
    assert limiter.cur_remaining(DEFAULT_USER_ID) == DEFAULT_RPS

    # test current quota remaining after group quota-limit request
    quota_remaining = _validate_group_process_request(limiter)
    assert limiter.cur_remaining() == quota_remaining
    clock.sleep(1)
    assert limiter.cur_remaining() == DEFAULT_RPS


def test_remove_bucket_and_is_configured():
    # set up quota-limiter for testing remove_bucket() and is_configured()
    limiter = QuotaLimiter()

    # test removing bucket before configuring group/user limiter
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.remove_bucket()

    # test removing buckets after configuring group/user limiter
    limiter.configure_group_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    t().assertTrue(limiter.is_configured(Level.GROUP))
    t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))

    limiter.remove_bucket(Level.GROUP)
    limiter.remove_bucket(DEFAULT_USER_ID)

    t().assertFalse(limiter.is_configured(Level.GROUP))
    t().assertFalse(limiter.is_configured(DEFAULT_USER_ID))


def test_is_exhausted():
    # set up quota-limiter for testing is_exhausted()
    limiter = QuotaLimiter()

    # test is_exhausted() before configuring group/user limiter
    with pytest.raises(QuotaLimitConfigNotFound):
        limiter.is_exhausted()

    # test is_exhausted() buckets after configuring group/user limiter
    limiter.configure_group_limit(rps=DEFAULT_RPS)
    limiter.configure_limit(user_id=DEFAULT_USER_ID, rps=DEFAULT_RPS)

    for _ in range(DEFAULT_RPS):
        t().assertTrue(limiter.is_configured(Level.GROUP))
        t().assertTrue(limiter.is_configured(DEFAULT_USER_ID))

        limiter.process_request(Level.GROUP)
        limiter.process_request(DEFAULT_USER_ID)


def _validate_group_process_request(limiter):
    """Validate group level quota-limiter process request"""
    quota_remaining = DEFAULT_RPS

    t().assertTrue(limiter.process_request())

    quota_remaining -= 1
    assert limiter.quota_remaining() == quota_remaining

    t().assertTrue(limiter.process_request(Level.GROUP))
    quota_remaining -= 1

    assert limiter.quota_remaining() == quota_remaining
    return quota_remaining


def _validate_user_quota_limit_process_request(limiter):
    """Validate a user level quota-limiter process request"""
    for i in range(DEFAULT_RPS):
        t().assertTrue(limiter.process_request(DEFAULT_USER_ID))
    t().assertFalse(limiter.process_request(DEFAULT_USER_ID))
