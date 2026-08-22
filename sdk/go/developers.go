package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type DevelopersClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewDevelopersClient(baseURL string) *DevelopersClient {
	return &DevelopersClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
	}
}

func (c *DevelopersClient) ListProjects() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/v1/developers/projects", c.BaseURL))
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
