package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type DataFabricClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewDataFabricClient(baseURL string) *DataFabricClient {
	return &DataFabricClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *DataFabricClient) ListDataSources() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/data-sources", c.BaseURL))
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
