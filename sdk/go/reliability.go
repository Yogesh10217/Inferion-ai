package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ReliabilityClient struct {
	BaseURL string
	HTTPClient *http.Client
}

func NewReliabilityClient(baseURL string) *ReliabilityClient {
	return &ReliabilityClient{
		BaseURL: baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *ReliabilityClient) GetHealth() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/reliability/health", c.BaseURL))
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
