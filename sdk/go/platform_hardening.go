package sdk

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type PlatformHardeningClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewPlatformHardeningClient(baseURL string) *PlatformHardeningClient {
	return &PlatformHardeningClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *PlatformHardeningClient) RunAudit(tenantID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/platform-hardening/audit", c.BaseURL)
	payload := map[string]interface{}{"tenant_id": tenantID, "include_ast_scan": true}
	data, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(data))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Tenant-ID", tenantID)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}
