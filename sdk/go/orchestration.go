package llmengine

import (
	"context"
)

type OrchestrationClient struct {
	BaseURL string
	APIKey  string
}

func NewOrchestrationClient(baseURL, apiKey string) *OrchestrationClient {
	return &OrchestrationClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

type WorkflowResponse struct {
	Name           string `json:"name"`
	TenantID       string `json:"tenant_id"`
	LifecycleState string `json:"lifecycle_state"`
}

func (c *OrchestrationClient) CreateWorkflow(ctx context.Context, name, tenantID string) (*WorkflowResponse, error) {
	return &WorkflowResponse{
		Name:           name,
		TenantID:       tenantID,
		LifecycleState: "DRAFT",
	}, nil
}
