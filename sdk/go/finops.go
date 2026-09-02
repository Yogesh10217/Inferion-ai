package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type FinOpsClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewFinOpsClient(baseURL string) *FinOpsClient {
	return &FinOpsClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *FinOpsClient) GetCosts(tenantID string) ([]map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/finops/costs?tenant_id=%s", c.BaseURL, tenantID))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result []map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}
