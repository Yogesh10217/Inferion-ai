package sdk

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

// PlatformIntegrationClient for Phase 5.58 Platform Integration Fabric
type PlatformIntegrationClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewPlatformIntegrationClient(baseURL string, apiKey string) *PlatformIntegrationClient {
	return &PlatformIntegrationClient{
		BaseURL:    strings.TrimRight(baseURL, "/"),
		APIKey:     apiKey,
		HTTPClient: &http.Client{},
	}
}

func (c *PlatformIntegrationClient) setHeaders(req *http.Request, tenantID string) {
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Tenant-ID", tenantID)
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}
}

func (c *PlatformIntegrationClient) BuildContext(tenantID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/platform-integration/context", c.BaseURL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer([]byte("{}")))
	if err != nil {
		return nil, err
	}
	c.setHeaders(req, tenantID)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var res map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, err
	}
	return res, nil
}
