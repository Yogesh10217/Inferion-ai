package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type TeamsClient struct {
	BaseURL    string
	HTTPClient *http.Client
	APIKey     string
}

func NewTeamsClient(baseURL string, apiKey string) *TeamsClient {
	return &TeamsClient{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{},
		APIKey:     apiKey,
	}
}

func (c *TeamsClient) Create(name string, teamType string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/teams", c.BaseURL)
	payload := map[string]interface{}{
		"name":      name,
		"team_type": teamType,
	}
	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}

func (c *TeamsClient) Run(teamID string, goal string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/v1/teams/%s/run", c.BaseURL, teamID)
	payload := map[string]interface{}{
		"goal": goal,
	}
	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result, nil
}
