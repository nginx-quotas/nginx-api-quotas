# Requesting NGINX API Quotas

There are 2 types of rate limiting - short term and long term (quotas), each with different use cases. Short term rate limits are focused on handling bursty traffic, protecting servers and infrastructure from being overwhelmed. Whereas long term quotas are used to measure a consumer’s usage of APIs over a longer period of time (per hour, day or month). Unlike short term rate limits, quotas are not designed to prevent a spike from overwhelming the API service. They are used to regulate API usage ensuring API consumers honor the terms of contract.  

ACM customers want both short term and long term rate limiting. With quota management system, customers typically want to

- Block intentional abuse of APIs (scraping, spamming)
- Reduce unintentional abuse while allowing a customer’s usage to burst if needed
- Monetize APIs via metering and usage-based billing
- Enforce API terms of service (ToS) 

## Story
Customers want to limit the number of requests a user can make. They want to set quotas on users and instruct the API gateway to reject requests when the quota limit is reached. 

Quota is similar to rate limit but have longer periods. Example user can have 10,000 requests to the API per month. 

## Functional Requirements

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

## Workflow

- Configure a quota management system (QMS):
  - Install a QMS
  - Create a QMS cluster
  - Set up a QMS cluster
    
- Create a quota policy in ACM:

  **Data Structure for `quotas`:**

  | Name    | Type    | Quota     | Limit By | Zone Size | Throttle  |
  |---------|---------|-----------|----------|-----------|-----------|
  | quota-1 | global  | 50,000/M  | `user`   | 50M       | `strict`  | 
  | quota-2 | cluster | 30,000/D  | `user`   | 30M       | `monitor` | 
  | quota-3 | proxy   | 10,000/M  | `user`   | 10M       | `monitor` | 

  - **Quota Limit By** 
    - `user`
    - `custom`: TBD (e.g., `org`, `project`)

  - **Quota Throttle**:
    - `strict` : strict enforcement (reject requests)
    - `monitor`: handle requests over the usage limit (monitor) 
    - `notify` : handle requests over the usage limit (monitor & notify) TBD

- Set the quota on a per user:

  - Payload
    ```json
    {
      "name": "sub-1",
      "policy": "quota-1"
    }
    ```

  - Data Structure for `users_quotas`

    | User(sub) | Policy  | Remaining | Enable  |
    |-----------|---------|-----------|---------|
    | sub-1     | quota-1 |   45,000  | `true`  |
    | sub-2     | quota-1 |   25,000  | `true`  |
    | sub-3     | quota-3 |    5,000  | `false` |

- Headers related to limits can be sent back to client

  | Field Name          | Description                                 |
  |---------------------|---------------------------------------------|
  | `X-Quota-Limit`     | The quota in the current window             |
  | `X-Quota-Remaining` | The remaining quota in the current window,  |
  | `X-Quota-Reset`     | The time remaining in the current window, specified in UTC epoch time (in seconds) |

  **Example:**
  ```
  X-Quota-Limit    : 10000
  X-Quota-Remaining:  5000
  X-Quota-Reset    : 86400
  ```

- Additional Considerations:
  - How to reset the quota

## Capacity Estimation


## Engineering Plan
- Stand-Alone Quota Mgmt.
- Dev Portal Integration: Quota Request
- ACM Integration: Publish Users' Quota
- Quota Mgmt. for single API gateway
- Quota Mgmt. for multiple API gateways
- Distributed Quota Mgmt.
- NJS module
- C or Rust module
- Event Bus
- Customers' DBMSes Integration
