package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ResilienceClient struct {
	BaseURL    string
	APIKey     string
	TenantID   string
	HTTPClient *http.Client
}

func NewResilienceClient(baseURL, apiKey string) *ResilienceClient {
	return &ResilienceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		TenantID:   "default",
		HTTPClient: &http.Client{},
	}
}

func (c *ResilienceClient) RegisterService(serviceName, tier, region string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/resilience/services/register?service_name=%s&tier=%s&region=%s", c.BaseURL, serviceName, tier, region)
	req, err := http.NewRequest("POST", url, nil)
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

func (c *ResilienceClient) GetAnalytics() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/resilience/analytics/report", c.BaseURL)
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
