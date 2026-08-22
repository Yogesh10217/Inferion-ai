package llmengine

import (
	"context"
)

type DeveloperPlatformClient struct {
	BaseURL string
	APIKey  string
}

func NewDeveloperPlatformClient(baseURL, apiKey string) *DeveloperPlatformClient {
	return &DeveloperPlatformClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

type ProjectResponse struct {
	Name     string `json:"name"`
	TenantID string `json:"tenant_id"`
	Status   string `json:"status"`
}

func (c *DeveloperPlatformClient) CreateProject(ctx context.Context, name, tenantID string) (*ProjectResponse, error) {
	return &ProjectResponse{
		Name:     name,
		TenantID: tenantID,
		Status:   "ACTIVE",
	}, nil
}
