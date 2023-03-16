"""Test for Global Quota Limiter without Configuration"""

from core.common.exceptions import QuotaLimitConfigNotFound
from core.common.utils import FakeClock
from core.controller.quota_limiter import QuotaLimiter


def test_group_quota_limiter_without_pre_configuration():
    """
              Global Quota Limiter Test without Configuration

    +-----+--------------------+-----------------------------------------+
    | No. | API Request Time   | Result                                  |
    +-----+--------------------+-----------------------------------------+
    | 001 | 16414477550.594631 | The quota-limit policy is not configured |
    | 002 | 16414477551.611572 | The quota-limit policy is not configured |
    | 003 | 16414477552.616608 | The quota-limit policy is not configured |
    | 004 | 16414477553.622341 | The quota-limit policy is not configured |
    | 005 | 16414477554.630001 | The quota-limit policy is not configured |
    | 006 | 16414477555.683441 | The quota-limit policy is not configured |
    | 007 | 16414477556.71747  | The quota-limit policy is not configured |
    | 008 | 16414477557.72588  | The quota-limit policy is not configured |
    | 009 | 16414477558.73065  | The quota-limit policy is not configured |
    | 010 | 16414477559.74699  | The quota-limit policy is not configured |
    +-----+--------------------+-----------------------------------------+
    """
    clock = FakeClock(factor=10.0)
    quota_limiter = QuotaLimiter(clock)
    res = True

    print("\n            Global Quota Limiter Test without Configuration\n")
    print("+-----+--------------------+-----------------------------------------+")
    print("| No. | API Request Time   | Result                                  |")
    print("+-----+--------------------+-----------------------------------------+")
    for i in range(10):
        print(f"| {i+1:03} | {clock.stime()} |", end=" ")
        res = False
        try:
            res = quota_limiter.process_request()
            print(f"{res!s:>5}  |")
        except QuotaLimitConfigNotFound:
            print(f"{QuotaLimitConfigNotFound.description} |")
            clock.sleep(1.0)
    print("+-----+--------------------+-----------------------------------------+")


if __name__ == "__main__":
    test_group_quota_limiter_without_pre_configuration()
