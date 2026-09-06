package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type DataClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewDataClient(baseURL string) *DataClient {
	return &DataClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *DataClient) ListDatasets(tenantID string) ([]map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/data/datasets?tenant_id=%s", c.BaseURL, tenantID))
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
