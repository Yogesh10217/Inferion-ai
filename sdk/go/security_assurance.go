package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
)

type SecurityAssuranceService struct {
	client *Client
}

type SecurityAssetPayload struct {
	Name        string                 `json:"name"`
	AssetType   string                 `json:"asset_type"`
	Criticality string                 `json:"criticality"`
	Location    string                 `json:"location"`
	Owner       string                 `json:"owner"`
	Metadata    map[string]interface{} `json:"metadata"`
}

func (s *SecurityAssuranceService) RegisterAsset(ctx context.Context, tenantID string, payload SecurityAssetPayload) (map[string]interface{}, error) {
	buf, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequestWithContext(ctx, "POST", s.client.baseURL+"/v1/security/assets", bytes.NewReader(buf))
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

func (s *SecurityAssuranceService) EvaluatePosture(ctx context.Context, tenantID string) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", s.client.baseURL+"/v1/security/posture", nil)
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
