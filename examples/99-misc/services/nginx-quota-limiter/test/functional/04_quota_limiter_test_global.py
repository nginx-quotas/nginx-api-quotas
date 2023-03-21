"""Test for Global Quota Limiter"""

from core.common.constants import QuotaLimitLevel as Level
from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_group_quota_limiter():
    """
                Global Quota Limiter Test

    +-----+------------------+--------------------+--------+
    | No. | Quota Remainings | API Request Time   | Result |
    +-----+------------------+--------------------+--------+
    | 001 |                3 | 16412735141.19422  |  True  |
    | 002 |                2 | 16412735141.195211 |  True  |
    | 003 |                1 | 16412735141.1955   |  True  |
    | 004 |                0 | 16412735141.19574  | False  |
    |     | quota exhausted. | request-004 is denied.      |
    +-----+------------------+--------------------+--------+
    | 005 |                3 | 16412735142.22069  |  True  |
    | 006 |                2 | 16412735142.221241 |  True  |
    | 007 |                1 | 16412735142.221481 |  True  |
    | 008 |                0 | 16412735142.22168  | False  |
    |     | quota exhausted. | request-008 is denied.      |
    +-----+------------------+--------------------+--------+
    | 009 |                3 | 16412735143.22465  |  True  |
    | 010 |                2 | 16412735143.225239 |  True  |
    +-----+------------------+--------------------+--------+
    """
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    quota_limit = 3
    res = True
    quota_limiter.configure_group_limit(rps=quota_limit)

    print("\n              Global Quota Limiter Test\n")
    print("+-----+------------------+--------------------+--------+")
    print("| No. | Quota Remainings | API Request Time   | Result |")
    print("+-----+------------------+--------------------+--------+")
    for i in range(10):
        remaining = quota_limiter.cur_remaining(Level.GROUP)
        print(f"| {i+1:03} | {remaining:16} | {clock.stime()} |", end=" ")
        res = quota_limiter.process_request()
        print(f"{res!s:>5}  |")
        if not res and quota_limiter.is_exhausted():
            print("|     | quota exhausted. |" +
                  f" request-{i+1:03} is denied.      |")
            print("+-----+------------------+--------------------+--------+")
            clock.sleep(1.0)
    if res:
        print("+-----+------------------+--------------------+--------+")


if __name__ == "__main__":
    test_group_quota_limiter()
