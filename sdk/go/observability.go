package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ObservabilityClient struct {
	BaseURL    string
	HTTPClient *http.Client
	APIKey     string
}

func NewObservabilityClient(baseURL string, apiKey string) *ObservabilityClient {
	return &ObservabilityClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
		APIKey:     apiKey,
	}
}

func (c *ObservabilityClient) GetTrace(traceID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/observability/traces/%s", c.BaseURL, traceID)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ObservabilityClient) GetExecution(executionID string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/observability/executions/%s", c.BaseURL, executionID)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ObservabilityClient) Replay(executionID string, forceExternalEffects bool) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/observability/executions/%s/replay", c.BaseURL, executionID)
	payload := map[string]interface{}{"force_external_effects": forceExternalEffects}
	body, _ := json.Marshal(payload)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ObservabilityClient) GetCosts() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/observability/costs", c.BaseURL)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ObservabilityClient) GetPerformance(component string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/observability/performance?component=%s", c.BaseURL, component)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *ObservabilityClient) GetStatus() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/operations/status", c.BaseURL)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}
