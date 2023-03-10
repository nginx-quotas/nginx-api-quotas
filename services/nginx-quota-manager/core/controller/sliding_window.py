"""TBD: Sliding Window Counter for Rate Limiter

Note that the algorithm is being tested and refactored which is to provide
same functions such as bucket algorithm. But test result would be not exactly
same as the bucket algorithm as this algorithm is not-so-strict. So this code
is just kept to refactor main algorthm and unit/functional/integration testing
codes for the future.
"""

import time


class RateLimitSlidingWindowCounter:

    def __init__(self, quota_limit, time_window, clock=time):
        self._quota_limit = quota_limit
        self._time_window = time_window
        self._clock = clock
        self.clear(quota_limit)

    def clear(self, pre_cnt):
        self._quota_remaining = self._quota_limit
        self._last_update_time = self._clock.time()
        self._pre_cnt = pre_cnt
        self._cur_cnt = 0

    def decrement(self):
        time_passed, res = self.is_enough_time_window()
        if res:
            self.clear(self._cur_cnt)

        time_remained = self._time_window - time_passed
        estimated_cnt = (
            self._pre_cnt * time_remained / self._time_window
        ) + self._cur_cnt

        if (estimated_cnt >= self._quota_limit):
            return False

        self._cur_cnt += 1
        self._quota_remaining = int(estimated_cnt)
        return True

    def is_enough_time_window(self):
        time_passed = self._clock.time() - self._last_update_time
        return time_passed, time_passed > self._time_window

    def cur_remaining(self):
        _, res = self.is_enough_time_window()
        return self._quota_limit if res else self._quota_remaining

    def quota_limit(self):
        return self._quota_limit

    def quota_remaining(self):
        return self._quota_remaining
