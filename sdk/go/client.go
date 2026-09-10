package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type Config struct {
	BaseURL        string
	APIKey         string
	OrganizationID string
	Timeout        time.Duration
}

type Client struct {
	Knowledge         *KnowledgeClient
	Architecture      *ArchitectureClient
	Compliance        *ComplianceClient
	Portfolio         *PortfolioClient
	Decisions         *DecisionsClient
	Reliability       *ReliabilityClient
	Security          *SecurityClient
	AILifecycle       *AILifecycleClient
	Events            *EventsClient
	Access            *AccessClient
	Data              *DataClient
	Identities        *IdentityAssuranceService
	Operations        *OperationsAssuranceService
	SecurityAssurance *SecurityAssuranceService

	BaseURL    string
	HTTPClient *http.Client

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
	httpClient := &http.Client{Timeout: cfg.Timeout}
	c := &Client{
		BaseURL:    cfg.BaseURL,
		HTTPClient: httpClient,
		baseURL:    cfg.BaseURL,
		apiKey:     cfg.APIKey,
		orgID:      cfg.OrganizationID,
		hc:         httpClient,
	}
	c.Knowledge = &KnowledgeClient{client: c}
	c.Architecture = &ArchitectureClient{client: c}
	c.Compliance = &ComplianceClient{client: c}
	c.Portfolio = &PortfolioClient{client: c}
	c.Decisions = &DecisionsClient{client: c}
	c.Reliability = &ReliabilityClient{client: c}
	c.Security = &SecurityClient{client: c}
	c.AILifecycle = &AILifecycleClient{client: c}
	c.Events = &EventsClient{client: c}
	c.Access = NewAccessClient(c.baseURL, c.apiKey)
	c.Data = NewDataClient(c.baseURL)
	c.Identities = &IdentityAssuranceService{client: c}
	c.Operations = &OperationsAssuranceService{client: c}
	c.SecurityAssurance = &SecurityAssuranceService{client: c}

	return c
}

func (c *Client) Do(req *http.Request) (*http.Response, error) {
	if req.Header.Get("Content-Type") == "" && req.Method != "GET" {
		req.Header.Set("Content-Type", "application/json")
	}
	if c.apiKey != "" && req.Header.Get("X-API-Key") == "" && req.Header.Get("Authorization") == "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}
	if c.orgID != "" && req.Header.Get("X-Organization-ID") == "" {
		req.Header.Set("X-Organization-ID", c.orgID)
	}
	return c.hc.Do(req)
}

func (c *Client) do(ctx context.Context, method, path string, body, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return err
		}
		bodyReader = bytes.NewReader(buf)
	}

	url := c.baseURL + path
	if !strings.HasPrefix(path, "http") && !strings.HasPrefix(path, "/") {
		url = c.baseURL + "/" + path
	}

	req, err := http.NewRequestWithContext(ctx, method, url, bodyReader)
	if err != nil {
		return err
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
		return err
	}
	defer res.Body.Close()

	if res.StatusCode >= 400 {
		return fmt.Errorf("request failed with status: %d", res.StatusCode)
	}

	if result != nil {
		return json.NewDecoder(res.Body).Decode(result)
	}
	return nil
}

func (c *Client) post(ctx context.Context, path string, body, result interface{}) error {
	return c.do(ctx, http.MethodPost, path, body, result)
}

func (c *Client) get(ctx context.Context, path string, result interface{}) error {
	return c.do(ctx, http.MethodGet, path, nil, result)
}

func (c *Client) Post(ctx context.Context, path string, body, result interface{}) error {
	return c.do(ctx, http.MethodPost, path, body, result)
}

func (c *Client) Get(ctx context.Context, path string, result interface{}) error {
	return c.do(ctx, http.MethodGet, path, nil, result)
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
