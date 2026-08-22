package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type MarketplaceClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewMarketplaceClient(baseURL string) *MarketplaceClient {
	return &MarketplaceClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *MarketplaceClient) ListItems() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/marketplace/items", c.BaseURL))
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
