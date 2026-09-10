package llmengine

import (
	"context"
)

type IntegrationClient struct {
	BaseURL string
	APIKey  string
}

func NewIntegrationClient(baseURL, apiKey string) *IntegrationClient {
	return &IntegrationClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

type ConnectorResponse struct {
	ConnectorID string `json:"connector_id"`
	Name        string `json:"name"`
	Type        string `json:"connector_type"`
	TenantID    string `json:"tenant_id"`
	Status      string `json:"status"`
}

func (c *IntegrationClient) RegisterConnector(ctx context.Context, name, connectorType, externalSystemID, tenantID string) (*ConnectorResponse, error) {
	return &ConnectorResponse{
		ConnectorID: "conn_go_123",
		Name:        name,
		Type:        connectorType,
		TenantID:    tenantID,
		Status:      "ACTIVE",
	}, nil
}

func (c *IntegrationClient) CreateWorkflow(ctx context.Context, name, tenantID string) (*WorkflowResponse, error) {
	return &WorkflowResponse{
		WorkflowID: "wf_go_123",
		Name:       name,
		Status:     "DRAFT",
	}, nil
}
