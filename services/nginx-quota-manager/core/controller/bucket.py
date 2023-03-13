"""Token Bucket for Rate Limiter"""

import time


class RateLimitBucket:
    """Rate Limit Bucket to manage quota remaining for each key

    This bucket is created and managed per each key such as user-id or global
    system.

    The following use cases show how to calculate quota remaining:
    case 1.
        _quota_limit    : 5 ea.
        _quota_remaining: 5 ea.
        _time_window    : 1 sec

        +------------------+--------+-----+------------------+   +---------+
        | bucket data      | ---->  sliding time window -----------------> |
        +------------------+--------+-----+------------------+   +---------+
        | clock time (sec) | 0.0 ~ 0.5 ~ 1.0      ~      2.0 |...| 59 ~ 60 |
        +------------------+--------+-----+------------------+   +---------+
        | # of requests    | 2      |  0  |         0        |   |    0    |
        | time_allowance() | 0      |  0  |       1 ~ 2      |   |   60    |
        | _quota_remaining | 3      |  3  |         3        |   |    5    |
        | cur_remaining()  | 3      |  3  | 5=min(5,3+5~10*5)|   |    5    |
        +------------------+--------+-----+------------------+   +---------+

    case 2.
        _quota_limit    : 5  ea.
        _quota_remaining: 5  ea.
        _time_window    : 60 sec

        +------------------+--------+-----+------------------+   +---------+
        | bucket data      | ---->  sliding time window -----------------> |
        +------------------+--------+-----+------------------+   +---------+
        | clock time (sec) | 0.0 ~ 0.5 ~ 1.0      ~      2.0 |...| 59 ~ 60 |
        +------------------+--------+-----+------------------+   +---------+
        | # of requests    | 2      |  0  |         0        |   |    0    |
        | time_allowance() | 0      |  0  |         0        |   |    1    |
        | _quota_remaining | 3      |  3  |         3        |   |    5    |
        | cur_remaining()  | 3      |  3  | 3 = min(5,3+0*5) |   |    5    |
        +------------------+--------+-----+------------------+   +---------+
    """

    def __init__(self, quota_limit, time_window, clock=time):
        """Set request-quota limit associated to a client in time-window(sec).

        Attributes:
            _quota_limit: A boolean indicating the maximum number of requests
                          per time window. (e.g. requests per second: rps)
            _time_window: An integer second which is an window size to track
                          fixed window (e.g. 1, 60 or 3600 seconds).
            _clock      : A time object to use either real or fake clock.
        """
        self._quota_limit = quota_limit
        self._time_window = time_window
        self._clock = clock
        self.clear()

    def clear(self):
        """Initialize quota remaining and last update time either when creating
           this bucket or if quota remaining is greater than quota limit."""
        self._quota_remaining = self._quota_limit
        self._last_update_time = self._clock.time()

    def decrement(self):
        """Reduce the quota remaining."""
        time_allowance = self.time_allowance()
        self._quota_remaining += time_allowance * self._quota_limit
        self._last_update_time += time_allowance * self._time_window

        if self._quota_remaining >= self._quota_limit:
            self.clear()

        if self._quota_remaining < 1:
            return False

        self._quota_remaining -= 1
        return True

    def time_allowance(self):
        """Return the number of seconds until the quota resets."""
        time_passed = self._clock.time() - self._last_update_time
        return int(time_passed // self._time_window)

    def cur_remaining(self):
        """Return updated quota remainining as current time is changed."""
        return min(
            self._quota_limit,
            self._quota_remaining + self.time_allowance() * self._quota_limit)

    def quota_limit(self):
        """Return quota limit.

        This can be refactored as the concept of adaptor which is switched to
        either remote cache server w/ key/value store or in-memory data in this
        class.

        So developers can just call this function to get the latest quota limit
        which can be changed by any admin via distributed rate-limiter apps."""
        return self._quota_limit

    def quota_remaining(self):
        """This is to return quota remainining for the time right after the
           process_request() is called in the rate-limiter.."""
        return self._quota_remaining
