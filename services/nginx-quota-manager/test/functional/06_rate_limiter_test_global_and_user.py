"""Test for Global and User Level Rate Limiter"""

from core.common.constants import RateLimitLevel as Level
from core.common.utils import FakeClock
from core.controller.rate_limiter import RateLimiter


def test_global_and_user_rate_limiter():
    """
            Both Global/User Rate Limiter Test

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
    rate_limiter = RateLimiter(clock)
    res = True
    rate_limiter.configure_global_limit(rps=5)
    rate_limiter.configure_limit(user_id=user_id, rps=3)

    print("\n           Both Global/User Rate Limiter Test\n")
    print("+-----+------------------+--------------------+--------+")
    print("| No. | Quota Remainings | API Request Time   | Result |")
    print("|     +---------+--------+                    |        |")
    print("|     | Global  |  User  |                    |        |")
    print("+-----+---------+--------+--------------------+--------+")
    for i in range(10):
        g_r = rate_limiter.cur_remaining(Level.GLOBAL)
        u_r = rate_limiter.cur_remaining(user_id)
        stime = clock.stime()
        print(f"| {i+1:03} | {g_r:5}   | {u_r:4}   | {stime} |", end=" ")
        res = rate_limiter.process_request(user_id)
        print(f"{res!s:>5}  |")
        if not res and rate_limiter.is_exhausted(user_id):
            print("|     | quota exhausted. |" +
                  f" request-{i+1:03} is denied.      |")
            print("+-----+---------+--------+--------------------+--------+")
            clock.sleep(1.0)
    if res:
        print("+-----+---------+--------+--------------------+--------+")


if __name__ == "__main__":
    test_global_and_user_rate_limiter()
