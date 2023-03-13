"""Rate Limiter Client Sample Code"""

from core.common.utils import str_time
from core.controller.rate_limiter import RateLimiter
from time import time, sleep


def sample_rate_limiter_client():
    """Sample code to show how to implement rate limiter"""
    my_user_id = "your-user-id"
    quota_limit = 3

    # 1. Create a rate limiter, and configure a quota limit for a user
    rate_limiter = RateLimiter()
    rate_limiter.configure_limit(user_id=my_user_id, rps=quota_limit)

    # 2. Request a rate-limit process
    for i in range(10):

        # Test current remaining from the limiter for the user
        req_time = str_time(time())
        remaining = rate_limiter.cur_remaining(my_user_id)

        # Request a rate-limit process for the user. Assume that you call this
        # before calling any API. This function is called by one of endpoints
        # in the Rate Limiter App so that it can be executed via API gateway.
        res = rate_limiter.process_request(my_user_id)
        print(f"{i+1:03}. remaining: {remaining}, {req_time:18s}, {res!s:>5}")

        # Check if the rate-limiter is exhausted for the user.
        if not res and rate_limiter.is_exhausted(my_user_id):
            print(f"     quota exhausted: request-{i+1:03} is denied\n")
            sleep(1)


if __name__ == "__main__":
    sample_rate_limiter_client()
