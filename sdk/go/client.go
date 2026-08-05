package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Config struct {
	BaseURL        string
	APIKey         string
	OrganizationID string
	Timeout        time.Duration
}

type Client struct {
	Knowledge *KnowledgeClient
	baseURL string
	apiKey  string
	orgID   string
	hc      *http.Client
}

func NewClient(cfg Config) *Client {
	if cfg.BaseURL == "" {
		cfg.BaseURL = "http://localhost:8000"
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 30 * time.Second
	}
	c := &Client{
		baseURL: cfg.BaseURL,
		apiKey:  cfg.APIKey,
		orgID:   cfg.OrganizationID,
		hc:      &http.Client{Timeout: cfg.Timeout},
	}
	c.Knowledge = &KnowledgeClient{client: c}
	return c,
	}
}

func (c *Client) Health(ctx context.Context) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/health", nil)
	if err != nil {
		return nil, err
	}
	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(res.Body).Decode(&result)
	return result, err
}

func (c *Client) CreateChatCompletion(ctx context.Context, body ChatCompletionRequest) (*ChatCompletionResponse, error) {
	buf, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/v1/chat/completions", bytes.NewReader(buf))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}
	if c.orgID != "" {
		req.Header.Set("X-Organization-ID", c.orgID)
	}

	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode >= 400 {
		return nil, fmt.Errorf("request failed with status: %d", res.StatusCode)
	}

	var resp ChatCompletionResponse
	err = json.NewDecoder(res.Body).Decode(&resp)
	return &resp, err
}
