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
	fmt.Println("| Test-Case | Upload an image by user-01. (quota: 1)     |")
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

	req.Header.Add("Cookie", "user_id=user-01")
	req.Header.Set("Content-Type", writer.FormDataContentType())

	retryCnt := 5
	quotaLimit := 1
	successCnt := 0
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
		if res.StatusCode == 200 {
			successCnt += 1
		}
		fmt.Println(string(body))
		fmt.Printf("- Attempting Count: %v\n", i+1)
		fmt.Printf("- Response Code: %v\n", res.StatusCode)
		fmt.Println("- Uploaded an image for an user-02. \n")
	}
	fmt.Printf("Result for uploading an image by user-01:\n")
	fmt.Printf("+---------------------------------------------------------+\n")
	fmt.Printf("| - Quota limit      per a second: %v %21s|\n", quotaLimit, " ")
	fmt.Printf("| - Allowed Requests per a second: %v %21s|\n", quotaLimit, " ")
	msg := "| - There are some error rates to manage quota limit.     |"
	if quotaLimit == successCnt {
		msg = "| - Successfully managed quota limit by rate-limiter.     |"
	}
	fmt.Println(msg)
	fmt.Printf("+---------------------------------------------------------+\n")
}
