package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type AgentsClient struct {
	client  *http.Client
	baseURL string
	apiKey  string
}

func NewAgentsClient(baseURL string, apiKey string) *AgentsClient {
	return &AgentsClient{
		client:  &http.Client{},
		baseURL: baseURL,
		apiKey:  apiKey,
	}
}

func (c *AgentsClient) RegisterAgent(tenantID string, name string, agentType string, role string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"name":       name,
		"agent_type": agentType,
		"role":       role,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/agents/register?tenant_id=%s", c.baseURL, tenantID), bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var res map[string]interface{}
	err = json.Unmarshal(respBody, &res)
	return res, err
}

func (c *AgentsClient) ExecuteTask(tenantID string, goal string, prompt string, agentID string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"goal":     goal,
		"prompt":   prompt,
		"agent_id": agentID,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/agents/execute?tenant_id=%s", c.baseURL, tenantID), bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var res map[string]interface{}
	err = json.Unmarshal(respBody, &res)
	return res, err
}
