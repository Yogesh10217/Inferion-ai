package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type Decision struct {
	ID               string                 `json:"id"`
	TenantID         string                 `json:"tenant_id"`
	Title            string                 `json:"title"`
	Description      string                 `json:"description,omitempty"`
	State            string                 `json:"state"`
	DecisionType     string                 `json:"decision_type"`
	Scope            string                 `json:"scope"`
	RiskLevel        string                 `json:"risk_level"`
	ConfidenceScore  float64                `json:"confidence_score"`
	UncertaintyScore float64                `json:"uncertainty_score"`
	CreatedAt        string                 `json:"created_at"`
	UpdatedAt        string                 `json:"updated_at"`
	Fingerprint      string                 `json:"fingerprint,omitempty"`
	Metadata         map[string]interface{} `json:"metadata"`
}

type DecisionClient struct {
	client   *Client
	BaseURL  string
	APIKey   string
	TenantID string
	HTTP     *http.Client
}

type DecisionsClient = DecisionClient

func NewDecisionClient(baseURL, apiKey, tenantID string) *DecisionClient {
	if baseURL == "" {
		baseURL = "http://localhost:8000"
	}
	if tenantID == "" {
		tenantID = "default"
	}
	return &DecisionClient{
		BaseURL:  baseURL,
		APIKey:   apiKey,
		TenantID: tenantID,
		HTTP:     &http.Client{},
	}
}

func (c *DecisionClient) CreateDecision(title, description, decisionType string) (*Decision, error) {
	url := fmt.Sprintf("%s/v1/decisions", c.BaseURL)
	payload := map[string]string{
		"title":         title,
		"description":   description,
		"decision_type": decisionType,
	}
	body, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Tenant-ID", c.TenantID)
	if c.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.APIKey)
	}

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error: %s", resp.Status)
	}

	var dec Decision
	if err := json.NewDecoder(resp.Body).Decode(&dec); err != nil {
		return nil, err
	}
	return &dec, nil
}
