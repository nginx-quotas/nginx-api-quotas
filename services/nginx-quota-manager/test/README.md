# How To Test Rate Limiter

## Prerequisites

### Setting Python Environment Variable PYTHONPATH on Mac
To set the python environment variable PYTHONPATH on Mac, follow the given steps:

- Step 1: Open the Terminal.
- Step 2: In your text editor, open the `~/.bash_profile` file. For example: vi `~/.bash_profile`;
- Step 3: To this file, add the following line at the bottom: 
  ```bash
  export PYTHONPATH="/Users/my_user/xxx/rate-limiter/01-solution/services/rate-limiter/"
  ```
- Step 4: Save this text editor file.
- Step 5: Close the terminal.
- Step 6: Restart the terminal. You can now read the new settings. Type:
  ```bash
  echo $PYTHONPATH
  ```

It would show something like `/Users/my_user/xxx/rate-limiter/01-solution/services/rate-limiter/`. That is it. `PYTHONPATH` is set. 

## Unit Test

**option 1:**
```bash
$ cd unit
$ python {your python file}
```

**option 2**
```bash
$ cd {root path of this repo}
$ make unit-test
```


## Functional Test

**option 1:**
```bash
$ cd functional
$ python {your python file}
$ bash run_test.sh
```

**option 2**
```bash
$ cd {root path of this repo}
$ make functional-test
```


## Integration Test

**option 1**

```bash
$ cd integration
$ go run {your go file}
```

**option 1**
```bash
$ cd {root path of this repo}
$ make integration-test
```


## E2E Test
You could this [this doc](./end_to_end) for your end-to-end test among API Gateway, Rate Limiter, and Upload App.
