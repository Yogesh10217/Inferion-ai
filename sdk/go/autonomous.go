package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type AutonomousAssuranceClient struct {
	client  *Client
	baseURL string
}

func NewAutonomousAssuranceClient(client *Client) *AutonomousAssuranceClient {
	return &AutonomousAssuranceClient{
		client:  client,
		baseURL: client.BaseURL + "/v1/autonomous",
	}
}

type CreateWorkflowRequest struct {
	Name               string `json:"name"`
	Description        string `json:"description,omitempty"`
	WorkflowType       string `json:"workflow_type,omitempty"`
	Priority           string `json:"priority,omitempty"`
	MaxDurationSeconds int    `json:"max_duration_seconds,omitempty"`
}

func (c *AutonomousAssuranceClient) CreateWorkflow(ctx context.Context, req CreateWorkflowRequest) (map[string]interface{}, error) {
	bodyBytes, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/workflows", bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("X-Tenant-ID", "default")

	resp, err := c.client.HTTPClient.Do(httpReq)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("autonomous assurance API error: status %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result, nil
}
