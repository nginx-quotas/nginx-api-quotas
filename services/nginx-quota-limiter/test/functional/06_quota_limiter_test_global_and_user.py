"""Test for Global and User Level Quota Limiter"""

from core.common.constants import QuotaLimitLevel as Level
from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_group_and_user_quota_limiter():
    """
            Both Global/User Quota Limiter Test

    +-----+------------------+--------------------+--------+
    | No. | Quota Remainings | API Request Time   | Result |
    |     +---------+--------+                    |        |
    |     | Global  |  User  |                    |        |
    +-----+---------+--------+--------------------+--------+
    | 001 |     5   |    3   | 16412735450.55083  |  True  |
    | 002 |     5   |    2   | 16412735450.551521 |  True  |
    | 003 |     5   |    1   | 16412735450.551832 |  True  |
    | 004 |     5   |    0   | 16412735450.55211  | False  |
    |     | quota exhausted. | request-004 is denied.      |
    +-----+---------+--------+--------------------+--------+
    | 005 |     5   |    3   | 16412735451.55554  |  True  |
    | 006 |     5   |    2   | 16412735451.556108 |  True  |
    | 007 |     5   |    1   | 16412735451.556301 |  True  |
    | 008 |     5   |    0   | 16412735451.55655  | False  |
    |     | quota exhausted. | request-008 is denied.      |
    +-----+---------+--------+--------------------+--------+
    | 009 |     5   |    3   | 16412735452.583208 |  True  |
    | 010 |     5   |    2   | 16412735452.58446  |  True  |
    +-----+---------+--------+--------------------+--------+
    """
    user_id = "shawn"
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    res = True
    quota_limiter.configure_group_limit(rps=5)
    quota_limiter.configure_limit(user_id=user_id, rps=3)

    print("\n           Both Global/User Quota Limiter Test\n")
    print("+-----+------------------+--------------------+--------+")
    print("| No. | Quota Remainings | API Request Time   | Result |")
    print("|     +---------+--------+                    |        |")
    print("|     | Global  |  User  |                    |        |")
    print("+-----+---------+--------+--------------------+--------+")
    for i in range(10):
        g_r = quota_limiter.cur_remaining(Level.GROUP)
        u_r = quota_limiter.cur_remaining(user_id)
        stime = clock.stime()
        print(f"| {i+1:03} | {g_r:5}   | {u_r:4}   | {stime} |", end=" ")
        res = quota_limiter.process_request(user_id)
        print(f"{res!s:>5}  |")
        if not res and quota_limiter.is_exhausted(user_id):
            print("|     | quota exhausted. |" +
                  f" request-{i+1:03} is denied.      |")
            print("+-----+---------+--------+--------------------+--------+")
            clock.sleep(1.0)
    if res:
        print("+-----+---------+--------+--------------------+--------+")


if __name__ == "__main__":
    test_group_and_user_quota_limiter()
