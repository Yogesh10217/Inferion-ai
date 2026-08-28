package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ControlAssuranceClient struct {
	BaseURL    string
	APIKey     string
	TenantID   string
	HTTPClient *http.Client
}

func NewControlAssuranceClient(baseURL, apiKey string) *ControlAssuranceClient {
	return &ControlAssuranceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		TenantID:   "default",
		HTTPClient: &http.Client{},
	}
}

func (c *ControlAssuranceClient) ListControls(category string) ([]map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/control-assurance/controls?category=%s", c.BaseURL, category)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("X-Tenant-ID", c.TenantID)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result []map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

func (c *ControlAssuranceClient) GetAnalytics() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/control-assurance/analytics", c.BaseURL)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("X-Tenant-ID", c.TenantID)

	resp, err := c.HTTPClient.Do(req)
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
