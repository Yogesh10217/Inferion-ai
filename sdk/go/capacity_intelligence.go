package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type CapacityIntelligenceClient struct {
	BaseURL    string
	APIKey     string
	HTTPClient *http.Client
}

func NewCapacityIntelligenceClient(baseURL string, apiKey string) *CapacityIntelligenceClient {
	return &CapacityIntelligenceClient{
		BaseURL:    baseURL,
		APIKey:     apiKey,
		HTTPClient: &http.Client{},
	}
}

func (c *CapacityIntelligenceClient) RegisterResource(tenantID string, resourceID string, name string, resourceType string, totalCapacity float64, capacityUnit string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/capacity/resources", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"resource_id":    resourceID,
		"name":           name,
		"resource_type":  resourceType,
		"total_capacity": totalCapacity,
		"capacity_unit":  capacityUnit,
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

func (c *CapacityIntelligenceClient) AssessCapacity(tenantID string, resourceID string, scope string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/capacity/assessments", c.BaseURL)
	body, _ := json.Marshal(map[string]interface{}{
		"resource_id": resourceID,
		"scope":       scope,
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
