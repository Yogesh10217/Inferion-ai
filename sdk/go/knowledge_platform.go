package llmengine

import (
	"context"
)

type KnowledgePlatformClient struct {
	BaseURL string
	APIKey  string
}

func NewKnowledgePlatformClient(baseURL, apiKey string) *KnowledgePlatformClient {
	return &KnowledgePlatformClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

type KnowledgeResponse struct {
	Title    string `json:"title"`
	TenantID string `json:"tenant_id"`
	Status   string `json:"status"`
}

func (c *KnowledgePlatformClient) CreateKnowledge(ctx context.Context, title, content, tenantID string) (*KnowledgeResponse, error) {
	return &KnowledgeResponse{
		Title:    title,
		TenantID: tenantID,
		Status:   "ACTIVE",
	}, nil
}
