package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ToolsClient struct {
	BaseURL    string
	HTTPClient *http.Client
	APIKey     string
}

func NewToolsClient(baseURL string, apiKey string) *ToolsClient {
	return &ToolsClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
		APIKey:     apiKey,
	}
}

type ToolMetadata struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Category    string  `json:"category"`
	Cost        float64 `json:"cost_estimate"`
}

type ToolResult struct {
	ExecutionID   string      `json:"execution_id"`
	ToolName      string      `json:"tool_name"`
	Status        string      `json:"status"`
	Output        interface{} `json:"output"`
	Error         string      `json:"error"`
	ExecutionTime float64     `json:"execution_time_seconds"`
}

func (c *ToolsClient) Create(name string, description string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/tools", c.BaseURL)
	payload := map[string]interface{}{
		"name":        name,
		"description": description,
	}
	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ToolsClient) List(tenantID string) ([]ToolMetadata, error) {
	url := fmt.Sprintf("%s/v1/tools?tenant_id=%s", c.BaseURL, tenantID)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var res map[string][]ToolMetadata
	json.NewDecoder(resp.Body).Decode(&res)
	return res["tools"], nil
}

func (c *ToolsClient) Execute(toolID string, params map[string]interface{}) (*ToolResult, error) {
	url := fmt.Sprintf("%s/v1/tools/%s/execute", c.BaseURL, toolID)
	payload := map[string]interface{}{
		"parameters": params,
	}
	body, _ := json.Marshal(payload)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var res map[string]ToolResult
	json.NewDecoder(resp.Body).Decode(&res)
	r := res["result"]
	return &r, nil
}
