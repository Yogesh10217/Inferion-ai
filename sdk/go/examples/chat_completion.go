package main

import (
	"fmt"
	"github.com/llm-engine/sdk-go"
)

func main() {
	client := llmengine.NewClient(llmengine.Config{
		BaseURL: "http://localhost:8000",
		APIKey:  "test_key",
	})
	fmt.Printf("Go SDK client initialized: %v\n", client)
}
