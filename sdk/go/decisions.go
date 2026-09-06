package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type Decision struct {
	DecisionID   string  `json:"decision_id"`
	TenantID     string  `json:"tenant_id"`
	Title        string  `json:"title"`
	Description  string  `json:"description,omitempty"`
	DecisionType string  `json:"decision_type"`
	Status       string  `json:"status"`
	Priority     string  `json:"priority"`
	Outcome      string  `json:"outcome,omitempty"`
	Confidence   float64 `json:"confidence"`
	RiskScore    float64 `json:"risk_score"`
}

type DecisionGovernanceService struct {
	client *Client
}

func (s *DecisionGovernanceService) CreateDecision(tenantID, title, decisionType, description string) (*Decision, error) {
	reqBody := map[string]interface{}{
		"title":         title,
		"decision_type": decisionType,
		"description":   description,
	}
	bodyBytes, _ := json.Marshal(reqBody)

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/decisions", s.client.BaseURL), bytes.NewBuffer(bodyBytes))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-tenant-id", tenantID)

	resp, err := s.client.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("decisions API error: %s", resp.Status)
	}

	var d Decision
	if err := json.NewDecoder(resp.Body).Decode(&d); err != nil {
		return nil, err
	}
	return &d, nil
}
