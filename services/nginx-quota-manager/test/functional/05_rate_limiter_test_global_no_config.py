"""Test for Global Rate Limiter without Configuration"""

from core.common.exceptions import RateLimitConfigNotFound
from core.common.utils import FakeClock
from core.controller.rate_limiter import RateLimiter


def test_global_rate_limiter_without_pre_configuration():
    """
              Global Rate Limiter Test without Configuration

    +-----+--------------------+-----------------------------------------+
    | No. | API Request Time   | Result                                  |
    +-----+--------------------+-----------------------------------------+
    | 001 | 16414477550.594631 | The rate-limit policy is not configured |
    | 002 | 16414477551.611572 | The rate-limit policy is not configured |
    | 003 | 16414477552.616608 | The rate-limit policy is not configured |
    | 004 | 16414477553.622341 | The rate-limit policy is not configured |
    | 005 | 16414477554.630001 | The rate-limit policy is not configured |
    | 006 | 16414477555.683441 | The rate-limit policy is not configured |
    | 007 | 16414477556.71747  | The rate-limit policy is not configured |
    | 008 | 16414477557.72588  | The rate-limit policy is not configured |
    | 009 | 16414477558.73065  | The rate-limit policy is not configured |
    | 010 | 16414477559.74699  | The rate-limit policy is not configured |
    +-----+--------------------+-----------------------------------------+
    """
    clock = FakeClock(factor=10.0)
    rate_limiter = RateLimiter(clock)
    res = True

    print("\n            Global Rate Limiter Test without Configuration\n")
    print("+-----+--------------------+-----------------------------------------+")
    print("| No. | API Request Time   | Result                                  |")
    print("+-----+--------------------+-----------------------------------------+")
    for i in range(10):
        print(f"| {i+1:03} | {clock.stime()} |", end=" ")
        res = False
        try:
            res = rate_limiter.process_request()
            print(f"{res!s:>5}  |")
        except RateLimitConfigNotFound:
            print(f"{RateLimitConfigNotFound.description} |")
            clock.sleep(1.0)
    print("+-----+--------------------+-----------------------------------------+")


if __name__ == "__main__":
    test_global_rate_limiter_without_pre_configuration()
