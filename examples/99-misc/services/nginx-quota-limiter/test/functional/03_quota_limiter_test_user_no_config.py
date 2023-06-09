"""Test for User Level Quota Limiter without Configuration"""

from core.common.exceptions import QuotaLimitConfigNotFound
from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_user_quota_limiter_without_pre_configuration():
    """
                User Quota Limiter Test without Configuration

    +-----+--------------------+------------------------------------------+
    | No. | API Request Time   | Result                                   |
    +-----+--------------------+------------------------------------------+
    | 001 | 16412584926.17527  | One of users quota-limit isn't configured |
    | 002 | 16412584927.22319  | One of users quota-limit isn't configured |
    | 003 | 16412584928.26035  | One of users quota-limit isn't configured |
    | 004 | 16412584929.298098 | One of users quota-limit isn't configured |
    | 005 | 16412584930.3393   | One of users quota-limit isn't configured |
    | 006 | 16412584931.36716  | One of users quota-limit isn't configured |
    | 007 | 16412584932.40036  | One of users quota-limit isn't configured |
    | 008 | 16412584933.42968  | One of users quota-limit isn't configured |
    | 009 | 16412584934.431301 | One of users quota-limit isn't configured |
    | 010 | 16412584935.43355  | One of users quota-limit isn't configured |
    +-----+--------------------+------------------------------------------+
    """
    user_id = "shawn"
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    res = True

    print("\n              User Quota Limiter Test without Configuration\n")
    print("+-----+--------------------+-----------------------------------------+")
    print("| No. | API Request Time   | Result                                  |")
    print("+-----+--------------------+-----------------------------------------+")
    for i in range(10):
        print(f"| {i+1:03} | {clock.stime()} |", end=" ")
        res = False
        try:
            res = quota_limiter.process_request(user_id)
            print(f"{res!s:>5}  |")
        except QuotaLimitConfigNotFound:
            print(f"{QuotaLimitConfigNotFound.description} |")
            clock.sleep(1.0)
    print("+-----+--------------------+-----------------------------------------+")


if __name__ == "__main__":
    test_user_quota_limiter_without_pre_configuration()
