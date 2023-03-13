package main

import (
  "fmt"
  "strings"
  "net/http"
  "io/ioutil"
)

func main() {

	fmt.Println("+-----------+--------------------------------------------+")
	fmt.Println("| Test-Case | Configuring a user-02 rate-limiter.        |")
	fmt.Println("+-----------+--------------------------------------------+\n")

	url := "http://127.0.0.1:12001/ratelimits/config/users/user-02"
	method := "PUT"

	payload := strings.NewReader(`{
		"quota_limit": 3,
		"limit_per": "rps"
	}`)

	client := &http.Client {}
	req, err := http.NewRequest(method, url, payload)
	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("Content-Type", "application/json")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(body))
	fmt.Printf("- Response Code: %v\n", res.StatusCode)
	fmt.Println("- Configured a user-02 rate-limiter. \n")
}