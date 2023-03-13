# Functional Test for Rate Limiter
Functional testing is a quality assurance process and a type of black-box testing that bases its test cases on the specifications of the software component under test. Functions are tested by feeding them input and examining the output, and internal program structure is rarely considered.

The functional test can be added into the CI/CD pipeline as one of automated stages. 
But, this repo provides 8 test cases to be able to locally run and check the result. So there are no assertions. You can feel free to add your codes for additional test cases to enhance test coverages. In addition to that, you could find [a sample code how to use a rate limiter](./01_rate_limiter_client_sample.py).

```
+--------------------------------------------------------+
|                                                        |
|                    Functional Test                     |
|                                                        |
|     (Rate Limiter Client -> Rate Limiter & Bucket)     |
|                                                        |
+--------------------------------------------------------+
```

### Table of Contents
- [Test Cases](#test-cases)
- [How To Run Test Cases](#how-to-run-test-cases)
- [Test Report Example](#test-report-example)


## Test Cases
1. [Sample Rate Limiter Client: Configuring Policy and Processing Request](./01_rate_limiter_client_sample.py)
2. [User Level Rate Limiter Test](./02_rate_limiter_test_user.py)
3. [User Rate Limiter Test without Configuration](./03_rate_limiter_test_user_no_config.py)
4. [Global Rate Limiter Test](./04_rate_limiter_test_global.py)
5. [Global Rate Limiter Test without Configuration](./05_rate_limiter_test_global_no_config.py)
6. [Both Global/User Rate Limiter Test](./06_rate_limiter_test_global_and_user.py)
7. [Both Global & 2 Users Rate Limiter Test](./07_rate_limiter_test_global_and_2_users.py)
8. [Both Global & 2 Users Rate Limiter Test With Different RPS](./08_rate_limiter_test_global_and_2_users_different_rps.py)

## How To Run Test Cases

> Option 1
```bash
$ export PYTHONPATH=/Users/{your-path}/rate-limiter/01-solution/services/rate-limiter
$ python {file name}
```

> Option 2
```bash
$ bash run_test.sh
```

> Option 3
```bash
$ cd {root path of this repo}
$ make functional-test
```

## [Test Report Example](./test-result_sample.txt)

### Simulation Result Example for Test Case 2:

```bash
$ python 02_rate_limiter_test_user.py

              User Level Rate Limiter Test

User ID: shawn
+-----+------------------+--------------------+--------+
| No. | Quota Remainings | API Request Time   | Result |
+-----+------------------+--------------------+--------+
| 001 |                3 | 16414732086.960781 |  True  |
| 002 |                2 | 16414732086.96167  |  True  |
| 003 |                1 | 16414732086.961899 |  True  |
| 004 |                0 | 16414732086.96209  | False  |
|     | quota exhausted. | request-004 is denied.      |
+-----+------------------+--------------------+--------+
| 005 |                3 | 16414732087.984068 |  True  |
| 006 |                2 | 16414732087.98513  |  True  |
| 007 |                1 | 16414732087.98559  |  True  |
| 008 |                0 | 16414732087.986    | False  |
|     | quota exhausted. | request-008 is denied.      |
+-----+------------------+--------------------+--------+
| 009 |                3 | 16414732088.989298 |  True  |
| 010 |                2 | 16414732088.990509 |  True  |
+-----+------------------+--------------------+--------+
```

### Simulation Result Example for Test Case 8:

```bash
$ python 08_rate_limiter_test_global_and_2_users_different_rps.py

      Both Global & 2 Users Rate Limiter Test With Different RPS

+-----+------------------------+--------------------+---------------+
|     |    Quota Remainings    |                    |    Result     |
| No. +--------+-------+-------+  API Request Time  +-------+-------+
|     | Global | User1 | User2 |                    | User1 | User2 |
+-----+--------+-------+-------+--------------------+-------+-------+
| 001 |    5   |    4  |    3  | 16414703829.56985  |  True |  True |
| 002 |    5   |    3  |    2  | 16414703829.57075  |  True |  True |
| 003 |    5   |    2  |    1  | 16414703829.57118  |  True |  True |
| 004 |    5   |    1  |    0  | 16414703829.57165  |  True | False |
|     | user-2 quota exhausted | request-004 is denied.             |
+-----+--------+-------+-------+--------------------+-------+-------+
| 005 |    5   |    0  |    0  | 16414703830.07682  | False | False |
|     | user-1 quota exhausted | request-005 is denied.             |
|     | user-2 quota exhausted | request-005 is denied.             |
+-----+--------+-------+-------+--------------------+-------+-------+
| 006 |    5   |    4  |    3  | 16414703831.102379 |  True |  True |
| 007 |    5   |    3  |    2  | 16414703831.10625  |  True |  True |
| 008 |    5   |    2  |    1  | 16414703831.107672 |  True |  True |
| 009 |    5   |    1  |    0  | 16414703831.109152 |  True | False |
|     | user-2 quota exhausted | request-009 is denied.             |
+-----+--------+-------+-------+--------------------+-------+-------+
| 010 |    5   |    0  |    0  | 16414703831.61685  | False | False |
|     | user-1 quota exhausted | request-010 is denied.             |
|     | user-2 quota exhausted | request-010 is denied.             |
+-----+--------+-------+-------+--------------------+-------+-------+
```
