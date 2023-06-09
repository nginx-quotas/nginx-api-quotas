# End-To-End (E2E) Test
End-to-end testing is a methodology used in the software development lifecycle (SDLC) to test the functionality and performance of an application under product-like circumstances and data to replicate live settings. The goal is to simulate what a real user scenario looks like from start to finish.

This repo does not provide automated `E2E Test` codes. However, you could manually test the following scenarios using sample `API Gateway`, `Quota-Limiter App`, and `Fake Upload App` after running Docker containers as follows.
- Configuring a group limit.
- Configuring a user limit.
- Processing limit request per each user.

For your convenience, you can also reuse the [Postman Collection](../postman/quota_limiter.postman_collection.json) to test the above scenarios via `Quota Limit APIs`.

**Run Docker containers: api-gateway, quota-limiter, fake upload-app**
```bash
$ cd {root path of this repo}
$ docker-compose up
```

**Check if Docker containers are being run**

Run `docker ps` or `docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Names}}"`:
```bash
CONTAINER ID   IMAGE                PORTS                    NAMES
1e94ab54e9ee   nginx-upload-app     0.0.0.0:9001->80/tcp     standalone-upload-app
87a2afa332d9   nginx-api-gateway    0.0.0.0:80->80/tcp       standalone-api-gateway
a06823693b3c   flask-quota-limiter   0.0.0.0:8001->8000/tcp   standalone-quota-limiter
```

**Configure a group quota-limit policy:**

```curl
curl  -i --request PUT 'http://127.0.0.1/quotalimit-config/group' \
      --header 'Content-Type: application/json' \
      --data-raw '{
        "quota_limit": 1,
        "limit_per": "rps"
      }'
```

**Configure a user-01 quota-limit policy:**

```curl
curl  -i --request PUT 'http://127.0.0.1/quotalimit-config/users/user-01' \
      --header 'Content-Type: application/json' \
      --data-raw '{
          "quota_limit": 1,
          "limit_per": "rps"
      }'
```

**Request a group quota-limit:**

```curl
$ curl -i --location --request GET 'http://127.0.0.1/quotalimit-decrement/group'
HTTP/1.1 200 OK

$ curl -i --location --request GET 'http://127.0.0.1/quotalimit-decrement/group'
HTTP/1.1 429 TOO MANY REQUESTS
```

**Request a user-01 quota-limit:**

```curl
$ curl -i --location --request GET 'http://127.0.0.1/quotalimit-decrement/users/user-01'
HTTP/1.1 200 OK

$ curl -i --location --request GET 'http://127.0.0.1/quotalimit-decrement/users/user-01'
HTTP/1.1 429 TOO MANY REQUESTS
```

**Upload a fake image for a user-01:**

```curl
$ curl -i --request POST 'http://127.0.0.1/images' \
          --header 'Cookie: user_id=user-01'
HTTP/1.1 201 Created

$ curl -i --request POST 'http://127.0.0.1/images' \
          --header 'Cookie: user_id=user-01'
HTTP/1.1 429 Too Many Requests
```
