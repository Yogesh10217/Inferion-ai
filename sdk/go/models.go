package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatCompletionRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float64   `json:"temperature,omitempty"`
	Stream      bool      `json:"stream,omitempty"`
}

type ChatChoice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason,omitempty"`
}

type ChatCompletionResponse struct {
	ID      string       `json:"id"`
	Object  string       `json:"object"`
	Created int64        `json:"created"`
	Model   string       `json:"model"`
	Choices []ChatChoice `json:"choices"`
}

type WorkflowResponse struct {
	WorkflowID     string `json:"workflow_id,omitempty"`
	Name           string `json:"name"`
	TenantID       string `json:"tenant_id,omitempty"`
	Status         string `json:"status,omitempty"`
	LifecycleState string `json:"lifecycle_state,omitempty"`
}

type ModelsService struct {
	client *Client
}

func (s *ModelsService) ListModels() (map[string]interface{}, error) {
	resp, err := http.Get(fmt.Sprintf("%s/v1/models", s.client.BaseURL))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}
