package llmengine

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type OperationalServiceReference struct {
	ServiceID   string `json:"service_id"`
	TenantID    string `json:"tenant_id"`
	Name        string `json:"name"`
	ServiceType string `json:"service_type"`
	Status      string `json:"status"`
}

type OperationsAssuranceService struct {
	client *Client
}

func (s *OperationsAssuranceService) RegisterService(tenantID, name, serviceType string) (*OperationalServiceReference, error) {
	payload := map[string]string{
		"name":         name,
		"service_type": serviceType,
	}
	body, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/v1/operations/services", s.client.BaseURL), bytes.NewBuffer(body))
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

	var svc OperationalServiceReference
	if err := json.NewDecoder(resp.Body).Decode(&svc); err != nil {
		return nil, err
	}
	return &svc, nil
}
