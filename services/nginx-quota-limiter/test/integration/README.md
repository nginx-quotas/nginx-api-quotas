# Integration Test for Quota Limiter
Integration testing is the phase in software testing in which individual software modules are combined and tested as a group. Integration testing is conducted to evaluate the compliance of a system or component with specified functional requirements. It occurs after unit testing and before system testing.

The integration test can be added into the CI/CD pipeline as one of automated stages. 
But, this repo provides 9 test cases to be able to locally run and check the result. So there are no assertions. You can feel free to add your codes for additional test cases to enhance test coverages.

```
+--------------------------------------------------------+
|                                                        |
|                    Integration Test                    |
|                                         Memory         |
|                                           |            |
|  (API Request --> API Gateway <-+-> Quota Limiter App)  |
|                                 |                      |
|                                 +-> Fake Upload App    |
|                                                        |
+--------------------------------------------------------+
```

### Table of Contents
- [Test Cases](#test-cases)
- [How To Run Test Cases](#how-to-run-test-cases)
- [Test Report Example](#test-report-example)


## Test Cases
1. [Configuring a group quota-limiter](./01_configure_group_limit.go)
2. [Configuring a user-01 quota-limiter](./02_configure_user_01_limit.go)
3. [Configuring a user-02 quota-limiter](./03_configure_user_02_limit.go)
4. [Upload an image by user-01. (quota: 1)](./04_upload_image_user_01.go)
5. [Upload an image by user-02. (quota: 3)](./05_upload_image_user_02.go)
6. [Upload an image by attacker](./06_upload_image_attacker.go)
7. [Delete a group quota limit configuration](./07_delete_group_limit_config.go)
8. [Delete a user_01 quota limit configuration](./08_delete_user_01_limit_config.go)
9. [Delete a user_02 quota limit configuration](./09_delete_user_02_limit_config.go)


## How To Run Test Cases

> **option 1**

```bash
$ go run {your go file}
```

> **option 2**

```bash
$ bash run_test.sh
```

> **option 3**
```bash
$ cd {root path of this repo}
$ make integration-test
```

## [Test Report Example](./test-result_sample.txt)

### Simulation Result Example for Test Case 1:

```
+-----------+--------------------------------------------+
| Test-Case | Configuring a group quota-limiter.         |
+-----------+--------------------------------------------+

{
    "quota_limit": 1,
    "limit_per": "rps",
    "bucket_name": "group",
    "quota_remaining": 1
}

- Response Code: 201
- Configured a group quota-limiter.
```

### Simulation Result Example for Test Case 4:

```
+-----------+--------------------------------------------+
| Test-Case | Upload an image by user-01. (quota: 1)     |
+-----------+--------------------------------------------+

{
    "user": user-01,
    "message": "an image file has been uploaded!"
}

- Attempting Count: 1
- Response Code: 200
- Uploaded an image for an user-02.

{"message": "quota exceeded"}

- Attempting Count: 2
- Response Code: 429
- Uploaded an image for an user-02.

{"message": "quota exceeded"}

- Attempting Count: 3
- Response Code: 429
- Uploaded an image for an user-02.

{"message": "quota exceeded"}

- Attempting Count: 4
- Response Code: 429
- Uploaded an image for an user-02.

{"message": "quota exceeded"}

- Attempting Count: 5
- Response Code: 429
- Uploaded an image for an user-02.

Result for uploading an image by user-01:
+---------------------------------------------------------+
| - Quota limit      per a second: 1                      |
| - Allowed Requests per a second: 1                      |
| - Successfully managed quota limit by quota-limiter.     |
+---------------------------------------------------------
```