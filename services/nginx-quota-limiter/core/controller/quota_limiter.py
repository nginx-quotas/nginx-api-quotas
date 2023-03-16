"""Quota Limiter for Managing Quota for Global System and All Users

Features:
=========
  1. Configuring group or user level quota-limit
  2. Processing quota-limit request
  3. Managing quota-limit buckets

Time and Space Complexity:
+------------+----------------------------------------------------------------+
| Assumption | - # of group limiters: 1                                       |
|            | - # of users          : N                                      |
|            | - range of N          : 0 <= N <= 500,000,000 (500M)           |
|            | - The requests-per-sec (rps) limit is set grouply or per-user. |
|            |   If both are set, only the user's limit should be used.       |
|            | - The quota limiter runs only on one machine in one process.   |
+------------+----------------------------------------------------------------+
| Time       |   Algorithm  | Insert | Search | Update | Delete               |
| Complexity | -------------+--------+--------+--------+--------              |
|            | - Average    | O(1)   | O(1)   | O(1)   | O(1)                 |
|            | - Worst Case | O(N)   | O(N)   | O(N)   | O(N)                 |
+------------+----------------------------------------------------------------+
| Space      | - Average    : O(N)                                            |
| Complexity | - Worst Case : O(N)                                            |
+------------+----------------------------------------------------------------+

Pros and Cons:
+------------+----------------------------------------------------------------+
| Pros       | - Time efficient                                               |
|            |   + buckets     : average CRUD O(1) for buckets                |
|            |   + each bucket : O(1), don't use queue, hash table            |
|            | - Memory efficient: don't manage real queue in each bucket.    |
|            | - Allows a burst for short periods than fixed window algorithm.|
|            | - Easy to reset available quota at the end of time window fits |
+------------+----------------------------------------------------------------+
| Cons       | - Minimum time window: 1 second (miliseconds aren't accurate.) |
|            |   e.g. requests: #1(0:000001), #2(0:999999) -> deny            |
|            |                  #1(0:000001), #2(1:000001) -> allow           |
|            |   There may have small error rate of floating point. But, it   |
|            |   would be normally allowed unless strict rule is required.    |
|            | - Additional bursts and delays are not supported.              |
|            | - Concurrent users requests + HA are not supported yet.        |
|            | - Limited types: multi types aren't supported per group/user.  |
+------------+----------------------------------------------------------------+

Future Improvements:
====================
  1. Functional Requirements:
     - Support multiple types per group and user.
       + Security/sys-performance: quota per second -> reject API requests.
       + Monetization: quota per month, year -> integrate w/ analytics.
       -> The current solution provides key/value bucket mangements so the ways
          of configuration and retrival might be refactored.

     - Enhance a burst and delay count if product requirements are needed.
       + As-is: The request needs be retried by clients if the reponse code is
                429 from quota-limiter that is to protect from malicious attack.
       + To-be: The quota-limiter handles proper amount of exceeded requests
                within some time window so that it would be smoother solution.

  2. Non-Functional Requirements for Scalability, Reliability, Security
     - Support a distributed quota-limiting solution.
     - Reduce the number of calls to distributed quota limiter.
     - Combine between an in-memory and distributed quota-limiter.

     e.g. - Add session mgmt and token validation integrating w/ IdP.
          - The API GW itself can use in-memory quota-limiter if it is to
            mitigate malicious attack. If it is for tracking quota for the
            purpose of monetization or data analytics, then we can combine
            both approaches between in-memory and distributed quota-limiters.
"""

from core.common.constants import (
    Duration as Dur,
    QuotaLimitAlgorithm as Algo,
    QuotaLimitLevel as Level
)
from core.common.exceptions import QuotaLimitConfigNotFound
from core.controller.bucket import QuotaLimitBucket
from core.controller.sliding_window import QuotaLimitSlidingWindowCounter
import time


class QuotaLimiter:
    """Quota Limiter for Managing Quota for Global System and All Users

    Attributes:
        buckets: An object indicating token buckets to manage each user quota.
        _clock: A time object to use either real clock or fake clock for test.
    """

    def __init__(self, clock=time, algorithm=Algo.TOKEN_BUCKET):
        self.buckets = {}
        self._clock = clock
        self._algorithm = algorithm

    def configure_group_limit(self, rps: int):
        """Configure group-level quota-limit policy in a bucket."""
        if self._algorithm == Algo.TOKEN_BUCKET:
            self.buckets[Level.GROUP] = QuotaLimitBucket(
                quota_limit=int(rps), time_window=Dur.SEC, clock=self._clock)
        else:
            self.buckets[Level.GROUP] = QuotaLimitSlidingWindowCounter(
                quota_limit=int(rps), time_window=Dur.SEC, clock=self._clock)

    def configure_limit(self, user_id, rps: int):
        """Configure user-level quota-limit policy in a bucket."""
        if self._algorithm == Algo.TOKEN_BUCKET:
            self.buckets[user_id] = QuotaLimitBucket(
                quota_limit=int(rps), time_window=Dur.SEC, clock=self._clock)
        else:
            self.buckets[user_id] = QuotaLimitSlidingWindowCounter(
                quota_limit=int(rps), time_window=Dur.SEC, clock=self._clock)

    def process_request(self, user_id=None) -> bool:
        """Reduce the quota remaining of either group or user quota-limit."""
        try:
            if user_id is None:
                return self.buckets[Level.GROUP].decrement()
            return self.buckets[user_id].decrement()
        except KeyError:
            raise QuotaLimitConfigNotFound

    def quota_limit(self, key=Level.GROUP):
        """Return the amount of quota limit within time window."""
        try:
            return self.buckets[key].quota_limit()
        except KeyError:
            raise QuotaLimitConfigNotFound

    def quota_remaining(self, key=Level.GROUP):
        """Return quota remainining once process_request() is called."""
        try:
            return self.buckets[key].quota_remaining()
        except KeyError:
            raise QuotaLimitConfigNotFound

    def cur_remaining(self, key=Level.GROUP):
        """Return updated quota remainining as current time is changed."""
        try:
            return self.buckets[key].cur_remaining()
        except KeyError:
            raise QuotaLimitConfigNotFound

    def remove_bucket(self, key=Level.GROUP):
        """Remove quota-limiter bucket by key"""
        try:
            del self.buckets[key]
        except KeyError:
            raise QuotaLimitConfigNotFound

    def is_configured(self, key=Level.GROUP):
        """Return if a quota-limiter bucket is configured by the key."""
        return True if key in self.buckets else False

    def is_exhausted(self, user_id=None):
        """Check if the quota-limiter is exhausted grouply or per-user."""
        if user_id is None:
            return self.quota_remaining(Level.GROUP) < 1
        return self.quota_remaining(user_id) < 1
