"""Test for Global and 2 Users Quota Limiter with Different Quota Limits"""

from core.common.constants import QuotaLimitLevel as Level
from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_group_and_2_users_different_rps_quota_limiter():
    """
        Both Global & 2 Users Quota Limiter Test With Different RPS

    +-----+------------------------+--------------------+---------------+
    |     |    Quota Remainings    |                    |    Result     |
    | No. +--------+-------+-------+  API Request Time  +-------+-------+
    |     | Global | User1 | User2 |                    | User1 | User2 |
    +-----+--------+-------+-------+--------------------+-------+-------+
    | 001 |    5   |    4  |    3  | 16412736272.78681  |  True |  True |
    | 002 |    5   |    3  |    2  | 16412736272.78749  |  True |  True |
    | 003 |    5   |    2  |    1  | 16412736272.78783  |  True |  True |
    | 004 |    5   |    1  |    0  | 16412736272.788181 |  True | False |
    |     | user-2 quota exhausted | request-004 is denied.             |
    +-----+--------+-------+-------+--------------------+-------+-------+
    | 005 |    5   |    0  |    0  | 16412736273.33049  | False | False |
    |     | user-1 quota exhausted | request-005 is denied.             |
    |     | user-2 quota exhausted | request-005 is denied.             |
    +-----+--------+-------+-------+--------------------+-------+-------+
    | 006 |    5   |    4  |    3  | 16412736274.41799  |  True |  True |
    | 007 |    5   |    3  |    2  | 16412736274.418509 |  True |  True |
    | 008 |    5   |    2  |    1  | 16412736274.419682 |  True |  True |
    | 009 |    5   |    1  |    0  | 16412736274.42093  |  True | False |
    |     | user-2 quota exhausted | request-009 is denied.             |
    +-----+--------+-------+-------+--------------------+-------+-------+
    | 010 |    5   |    0  |    0  | 16412736274.93911  | False | False |
    |     | user-1 quota exhausted | request-010 is denied.             |
    |     | user-2 quota exhausted | request-010 is denied.             |
    +-----+--------+-------+-------+--------------------+-------+-------+
    """
    user_id_01 = "user-1"
    user_id_02 = "user-2"
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    res1 = res2 = True
    quota_limiter.configure_group_limit(rps=5)
    quota_limiter.configure_limit(user_id=user_id_01, rps=4)
    quota_limiter.configure_limit(user_id=user_id_02, rps=3)

    _P("\n      Both Global & 2 Users Quota Limiter Test With Different RPS\n")
    _P("+-----+------------------------+--------------------+---------------+")
    _P("|     |    Quota Remainings    |                    |    Result     |")
    _P("| No. +--------+-------+-------+  API Request Time  +-------+-------+")
    _P("|     | Global | User1 | User2 |                    | User1 | User2 |")
    _P("+-----+--------+-------+-------+--------------------+-------+-------+")
    for i in range(10):
        gr = quota_limiter.cur_remaining(Level.GROUP)
        u1 = quota_limiter.cur_remaining(user_id_01)
        u2 = quota_limiter.cur_remaining(user_id_02)

        s_tm = clock.stime()
        print(f"| {i+1:03} | {gr:6} | {u1:5} | {u2:5} | {s_tm} |", end=" ")

        res1 = quota_limiter.process_request(user_id_01)
        res2 = quota_limiter.process_request(user_id_02)
        print(f"{res1!s:>5} | {res2!s:>5} |")

        exh1 = is_exhausted(i+1, res1, quota_limiter, user_id_01, clock, 0.5)
        exh2 = is_exhausted(i+1, res2, quota_limiter, user_id_02, clock, 0.5)
        if exh1 or exh2:
            _print_line()

    if not(res1 and res2):
        return
    _P("+-----+--------+-------+-------+--------------------+-------+-------+")


def _P(str):
    print(str)


def _print_line():
    _P("+-----+--------+-------+-------+--------------------+-------+-------+")


def is_exhausted(try_cnt, res, quota_limiter, user_id, clock, sleep_time):
    if not res and quota_limiter.is_exhausted(user_id):
        print(f"|     | {user_id} quota exhausted |" +
              f" request-{try_cnt:03} is denied.             |")
        clock.sleep(sleep_time)
        return True
    return False


if __name__ == "__main__":
    test_group_and_2_users_different_rps_quota_limiter()
