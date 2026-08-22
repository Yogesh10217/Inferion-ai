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

type IntegrationResponse struct {
	Name     string `json:"name"`
	Category string `json:"category"`
	TenantID string `json:"tenant_id"`
	Status   string `json:"status"`
}

func (c *IntegrationClient) RegisterIntegration(ctx context.Context, name, category, tenantID string) (*IntegrationResponse, error) {
	return &IntegrationResponse{
		Name:     name,
		Category: category,
		TenantID: tenantID,
		Status:   "ACTIVE",
	}, nil
}
