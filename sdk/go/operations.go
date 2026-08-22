package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type OperationsClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewOperationsClient(baseURL string) *OperationsClient {
	return &OperationsClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *OperationsClient) GetHealth() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/operations/health", c.BaseURL))
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
