package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {

	fmt.Println("+-----------+--------------------------------------------+")
	fmt.Println("| Test-Case | Configuring a user-01 quota-limiter.       |")
	fmt.Println("+-----------+--------------------------------------------+")

	url := "http://127.0.0.1:12001/quotalimits/config/users/user-01"
	method := "PUT"

	payload := strings.NewReader(`{
		"quota_limit": 1,
		"limit_per": "rps"
	}`)

	client := &http.Client{}
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
	fmt.Println("- Configured a user-01 quota-limiter. \n")
}
