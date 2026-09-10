package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ContinuousAssuranceClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewContinuousAssuranceClient(baseURL string, apiKey string) *ContinuousAssuranceClient {
	return &ContinuousAssuranceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		HTTPClient: &http.Client{},
	}
}

func (c *ContinuousAssuranceClient) RecordObservation(tenantID string, domain string, obsType string, payload map[string]interface{}) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/continuous-assurance/observations", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"source_domain":    domain,
		"observation_type": obsType,
		"payload":          payload,
	})

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
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
