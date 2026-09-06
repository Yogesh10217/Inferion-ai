package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type KnowledgeReference struct {
	ReferenceID    string `json:"reference_id"`
	TenantID       string `json:"tenant_id"`
	ExternalKey    string `json:"external_key"`
	ResourceType   string `json:"resource_type"`
	Status         string `json:"status"`
	Classification string `json:"classification"`
	SHA256Checksum string `json:"sha256_checksum"`
	IsImmutable    bool   `json:"is_immutable"`
}

type KnowledgeTrustAssessment struct {
	AssessmentID     string  `json:"assessment_id"`
	TenantID         string  `json:"tenant_id"`
	TargetResourceID string  `json:"target_resource_id"`
	OverallScore     float64 `json:"overall_score"`
	TrustBand        string  `json:"trust_band"`
}

type KnowledgeAssuranceService struct {
	client *Client
}

func (s *KnowledgeAssuranceService) GetStatus(tenantID string) (map[string]interface{}, error) {
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/v1/knowledge/status", s.client.BaseURL), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("x-tenant-id", tenantID)

	resp, err := s.client.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("knowledge status API error: %s", resp.Status)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

func (s *KnowledgeAssuranceService) CreateReference(tenantID, externalKey, resourceType, classification string) (*KnowledgeReference, error) {
	reqBody := map[string]interface{}{
		"external_key":   externalKey,
		"resource_type":  resourceType,
		"classification": classification,
	}
	bodyBytes, _ := json.Marshal(reqBody)

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/knowledge/references", s.client.BaseURL), bytes.NewBuffer(bodyBytes))
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
		return nil, fmt.Errorf("knowledge reference API error: %s", resp.Status)
	}

	var ref KnowledgeReference
	if err := json.NewDecoder(resp.Body).Decode(&ref); err != nil {
		return nil, err
	}
	return &ref, nil
}

func (s *KnowledgeAssuranceService) EvaluateTrust(tenantID, targetResourceID string) (*KnowledgeTrustAssessment, error) {
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/v1/knowledge/trust/%s", s.client.BaseURL, targetResourceID), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("x-tenant-id", tenantID)

	resp, err := s.client.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("knowledge trust API error: %s", resp.Status)
	}

	var trust KnowledgeTrustAssessment
	if err := json.NewDecoder(resp.Body).Decode(&trust); err != nil {
		return nil, err
	}
	return &trust, nil
}
