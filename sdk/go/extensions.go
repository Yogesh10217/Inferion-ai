package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ExtensionsClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewExtensionsClient(baseURL string) *ExtensionsClient {
	return &ExtensionsClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *ExtensionsClient) ListExtensions() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/extensions", c.BaseURL))
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
