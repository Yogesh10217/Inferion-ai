package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ControlPlaneClient struct {
	BaseURL string
	HTTPClient *http.Client
}

func NewControlPlaneClient(baseURL string) *ControlPlaneClient {
	return &ControlPlaneClient{
		BaseURL: baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *ControlPlaneClient) GetSummary() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/control-plane/summary", c.BaseURL))
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
