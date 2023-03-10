# nginx-monetization
NGINX Monetization Core Modules &amp; Examples for NGINX API Gateway and API Connectivity Management

## Use Cases
There are 2 types of rate limiting - short term and long term (quotas), each with different use cases. Short term rate limits are focused on handling bursty traffic, protecting servers and infrastructure from being overwhelmed. Whereas long term quotas are used to measure a consumer’s usage of APIs over a longer period of time (per hour, day or month). Unlike short term rate limits, quotas are not designed to prevent a spike from overwhelming the API service. They are used to regulate API usage ensuring API consumers honor the terms of contract.  

ACM customers want both short term and long term rate limiting. With quota management system, customers typically want to

- Block intentional abuse of APIs (scraping, spamming)
- Reduce unintentional abuse while allowing a customer’s usage to burst if needed
- Monetize APIs via metering and usage-based billing
- Enforce API terms of service (ToS) 

## Story
Customers want to limit the number of requests a user can make. They want to set quotas on users and instruct the API gateway to reject requests when the quota limit is reached. 

Quota is similar to rate limit but have longer periods. Example user can have 10,000 requests to the API per month. 

**Summary of the work:**

1. API owner can set the quota on a per user basis

2. Quotas are set at the API level. Access to any endpoint in the API decrements the count

3. When users quota exceeds the limit, the API gateway can be configured for either of the scenarios below

   3.1 strict enforcement (reject requests) or 

   3.2 handle requests over the usage limit (monitor and notify) 

4. Quotas can be reset

5. Quotas can be disabled

6. Headers related to limits can be sent back to client (remaining usage etc)

> **Notes:**
> 
> Checking for quota is expensive. Maintaining counters for each user is even more expensive. Suggest to look into event driven approach


## References
- [How to Set Quotas with NGINX Plus](https://www.youtube.com/watch?v=hqqOsXTG2L8)
- [Shared Caches with NGINX Plus Cache Clusters, Part1](https://www.nginx.com/blog/shared-caches-nginx-plus-cache-clusters-part-1/)
