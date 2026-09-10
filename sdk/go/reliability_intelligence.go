package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ReliabilityIntelligenceClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewReliabilityIntelligenceClient(baseURL string, apiKey string) *ReliabilityIntelligenceClient {
	return &ReliabilityIntelligenceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		HTTPClient: &http.Client{},
	}
}

func (c *ReliabilityIntelligenceClient) EvaluateServiceHealth(tenantID string, serviceID string, rawMetrics map[string]interface{}) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/reliability/health", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"service_id": serviceID,
		"metrics":    rawMetrics,
	})

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Tenant-ID", tenantID)
	if c.APIKey != "" {
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.APIKey))
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ReliabilityIntelligenceClient) PredictFailure(tenantID string, serviceID string, horizonMinutes int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/reliability/predictions", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"service_id":      serviceID,
		"horizon_minutes": horizonMinutes,
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
