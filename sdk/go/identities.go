package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type IdentityReference struct {
	IdentityID   string `json:"identity_id"`
	TenantID     string `json:"tenant_id"`
	Name         string `json:"name"`
	IdentityType string `json:"identity_type"`
	Category     string `json:"category"`
	Status       string `json:"status"`
	ExternalID   string `json:"external_id,omitempty"`
}

type IdentityTrustAssessment struct {
	AssessmentID string  `json:"assessment_id"`
	IdentityID   string  `json:"identity_id"`
	TenantID     string  `json:"tenant_id"`
	IsTrusted    bool    `json:"is_trusted"`
	RiskLevel    string  `json:"risk_level"`
}

type IdentityAssuranceService struct {
	client *Client
}

func (s *IdentityAssuranceService) RegisterIdentity(tenantID, name, identityType, category string) (*IdentityReference, error) {
	payload := map[string]string{
		"name":          name,
		"identity_type": identityType,
		"category":      category,
	}
	body, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/identities", s.client.BaseURL), bytes.NewBuffer(body))
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

	var identity IdentityReference
	if err := json.NewDecoder(resp.Body).Decode(&identity); err != nil {
		return nil, err
	}
	return &identity, nil
}
