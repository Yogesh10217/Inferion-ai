package tests

import (
	"testing"
	"github.com/llm-engine/sdk-go"
)

func TestNewClient(t *testing.T) {
	client := llmengine.NewClient(llmengine.Config{
		BaseURL: "http://localhost:8000",
		APIKey:  "my_api_key",
	})
	if client == nil {
		t.Fatal("Expected non-nil client")
	}
}
