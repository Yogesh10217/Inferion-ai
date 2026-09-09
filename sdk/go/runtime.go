package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type RuntimeIntelligenceClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewRuntimeIntelligenceClient(baseURL string, apiKey string) *RuntimeIntelligenceClient {
	return &RuntimeIntelligenceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		HTTPClient: &http.Client{},
	}
}

func (c *RuntimeIntelligenceClient) IngestObservation(tenantID string, subsystem string, metricName string, value float64, dimensions map[string]string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/runtime/observations", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"subsystem":   subsystem,
		"metric_name": metricName,
		"value":       value,
		"dimensions":  dimensions,
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

func (c *RuntimeIntelligenceClient) EvaluateHealth(tenantID string, subsystem string, rawTelemetry map[string]interface{}) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/runtime/health", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"subsystem":     subsystem,
		"raw_telemetry": rawTelemetry,
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
