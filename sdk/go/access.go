package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type AccessClient struct {
	BaseURL    string
	APIKey     string
	TenantID   string
	HTTPClient *http.Client
}

func NewAccessClient(baseURL, apiKey string) *AccessClient {
	return &AccessClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		TenantID:   "default",
		HTTPClient: &http.Client{},
	}
}

func (c *AccessClient) ListIdentities() ([]map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/access/identities", c.BaseURL)
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

func (c *AccessClient) GetAnalytics() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/access/analytics", c.BaseURL)
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
