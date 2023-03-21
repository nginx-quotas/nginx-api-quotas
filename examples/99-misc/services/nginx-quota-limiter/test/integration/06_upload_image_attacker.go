package main

import (
  "fmt"
  "bytes"
  "mime/multipart"
  "net/http"
  "io/ioutil"
)

func main() {

	fmt.Println("+-----------+--------------------------------------------+")
	fmt.Println("| Test-Case | Upload an image by attacker                |")
	fmt.Println("+-----------+--------------------------------------------+\n")

	url := "http://127.0.0.1:13001/images"
	method := "POST"

	payload := &bytes.Buffer{}
	writer := multipart.NewWriter(payload)
	err := writer.Close()
	if err != nil {
		fmt.Println(err)
		return
	}


	client := &http.Client {}
	req, err := http.NewRequest(method, url, payload)
	if err != nil {
		fmt.Println(err)
		return
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	retryCnt := 5
	userNotFoundCnt := 0
	for i := 0; i < retryCnt; i++ {
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
		if res.StatusCode == 404 {
			userNotFoundCnt += 1
		}
		fmt.Println(string(body))
		fmt.Printf("- Attempting Count: %v\n", i+1)
		fmt.Printf("- Response Code: %v\n", res.StatusCode)
	}
	fmt.Printf("\nResult for uploading an image by unknown user(attacker):\n")
	fmt.Printf("+----------------------------------------------------------+\n")
	fmt.Printf("| - API request count : %v %31s  |\n", retryCnt, " ")
	fmt.Printf("| - API rejected count: %v %31s  |\n", userNotFoundCnt, " ")
	msg := "| - An unknown user is allowed some API request(s).        |"
	if retryCnt == userNotFoundCnt {
		msg = "| - Successfully rejected unknown attackers' API requests. |"
	}
	fmt.Println(msg)
	fmt.Printf("+----------------------------------------------------------+\n")
}
