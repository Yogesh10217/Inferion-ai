package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
)

type UnifiedIntelligenceService struct {
	client *Client
}

type UnifiedSignalPayload struct {
	Domain             string                 `json:"domain"`
	EntityReference    string                 `json:"entity_reference"`
	SignalType         string                 `json:"signal_type"`
	Severity           string                 `json:"severity"`
	ConfidenceScore    float64                `json:"confidence_score"`
	RiskScore          float64                `json:"risk_score"`
	EvidenceReferences []string               `json:"evidence_references"`
	Metadata           map[string]interface{} `json:"metadata"`
	IdempotencyKey     string                 `json:"idempotency_key,omitempty"`
}

func (s *UnifiedIntelligenceService) IngestSignal(ctx context.Context, tenantID string, payload UnifiedSignalPayload) (map[string]interface{}, error) {
	buf, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequestWithContext(ctx, "POST", s.client.baseURL+"/v1/intelligence/signals", bytes.NewReader(buf))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-tenant-id", tenantID)

	res, err := s.client.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(res.Body).Decode(&result)
	return result, err
}

func (s *UnifiedIntelligenceService) EvaluateSituations(ctx context.Context, tenantID string) ([]map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "POST", s.client.baseURL+"/v1/intelligence/situations/evaluate", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("x-tenant-id", tenantID)

	res, err := s.client.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var result []map[string]interface{}
	err = json.NewDecoder(res.Body).Decode(&result)
	return result, err
}

func (s *UnifiedIntelligenceService) EvaluateRisk(ctx context.Context, tenantID string) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", s.client.baseURL+"/v1/intelligence/risk", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("x-tenant-id", tenantID)

	res, err := s.client.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(res.Body).Decode(&result)
	return result, err
}
