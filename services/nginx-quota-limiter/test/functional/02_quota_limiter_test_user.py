"""Test for User Level Quota Limiter"""

from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_user_level_quota_limiter():
    """test case: configure and request quota-limiter for 1 user

    Test Result Example:

                User Level Quota Limiter Test

    +-----+------------------+--------------------+--------+
    | No. | Quota Remainings | API Request Time   | Result |
    +-----+------------------+--------------------+--------+
    | 001 |                3 | 16412734796.33174  |  True  |
    | 002 |                2 | 16412734796.33234  |  True  |
    | 003 |                1 | 16412734796.332691 |  True  |
    | 004 |                0 | 16412734796.333    | False  |
    |     | quota exhausted. | request-004 is denied.      |
    +-----+------------------+--------------------+--------+
    | 005 |                3 | 16412734797.35062  |  True  |
    | 006 |                2 | 16412734797.35132  |  True  |
    | 007 |                1 | 16412734797.35155  |  True  |
    | 008 |                0 | 16412734797.35174  | False  |
    |     | quota exhausted. | request-008 is denied.      |
    +-----+------------------+--------------------+--------+
    | 009 |                3 | 16412734798.36992  |  True  |
    | 010 |                2 | 16412734798.370518 |  True  |
    +-----+------------------+--------------------+--------+
    """
    user_id = "shawn"
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    quota_limit = 3
    res = True
    quota_limiter.configure_limit(user_id=user_id, rps=quota_limit)

    print("\n              User Level Quota Limiter Test\n")
    print(f"User ID: {user_id}")
    print("+-----+------------------+--------------------+--------+")
    print("| No. | Quota Remainings | API Request Time   | Result |")
    print("+-----+------------------+--------------------+--------+")
    for i in range(10):
        remaining = quota_limiter.cur_remaining(user_id)
        print(f"| {i+1:03} | {remaining:16} | {clock.stime()} |", end=" ")
        res = quota_limiter.process_request(user_id)
        print(f"{res!s:>5}  |")
        if not res and quota_limiter.is_exhausted(user_id):
            print("|     | quota exhausted. |" +
                  f" request-{i+1:03} is denied.      |")
            print("+-----+------------------+--------------------+--------+")
            clock.sleep(1.0)
    if res:
        print("+-----+------------------+--------------------+--------+")


if __name__ == "__main__":
    test_user_level_quota_limiter()
