package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type PlanningClient struct {
	BaseURL    string
	HTTPClient *http.Client
	APIKey     string
}

func NewPlanningClient(baseURL string, apiKey string) *PlanningClient {
	return &PlanningClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
		APIKey:     apiKey,
	}
}

func (c *PlanningClient) Create(title string, description string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/plans", c.BaseURL)
	payload := map[string]interface{}{
		"title":       title,
		"description": description,
	}
	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
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
