package llmengine

import (
	"context"
	"fmt"
)

type ApplicationClient struct {
	baseURL string
	apiKey  string
}

func NewApplicationClient(baseURL, apiKey string) *ApplicationClient {
	return &ApplicationClient{
		baseURL: baseURL,
		apiKey:  apiKey,
	}
}

type ApplicationResponse struct {
	ApplicationID string `json:"application_id"`
	Name          string `json:"name"`
	AppType       string `json:"app_type"`
	Status        string `json:"status"`
	TenantID      string `json:"tenant_id"`
}

func (c *ApplicationClient) CreateApplication(ctx context.Context, name, appType, tenantID string) (*ApplicationResponse, error) {
	return &ApplicationResponse{
		ApplicationID: fmt.Sprintf("app_%s", name),
		Name:          name,
		AppType:       appType,
		Status:        "DRAFT",
		TenantID:      tenantID,
	}, nil
}
