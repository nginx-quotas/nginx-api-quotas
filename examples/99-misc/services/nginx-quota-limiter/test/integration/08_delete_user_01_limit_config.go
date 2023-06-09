package main

import (
	"fmt"
	"net/http"
)

func main() {

	fmt.Println("+-----------+---------------------------------------------+")
	fmt.Println("| Test-Case | Delete a user_01 quota limit configuration. |")
	fmt.Println("+-----------+---------------------------------------------+")

	url := "http://127.0.0.1:12001/quotalimits/config/users/user-01"
	method := "DELETE"

	client := &http.Client{}
	req, err := http.NewRequest(method, url, nil)

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
	fmt.Printf("- Response Code: %v\n", res.StatusCode)
	if res.StatusCode == 204 {
		fmt.Println("- Successfully deleted a group quota-limiter. \n")
	} else {
		fmt.Println("- Unable to delete a group quota-limiter. \n")
	}
}
