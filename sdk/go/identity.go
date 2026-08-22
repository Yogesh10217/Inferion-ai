package llmengine

import (
	"context"
)

type IdentityClient struct {
	BaseURL string
	APIKey  string
}

func NewIdentityClient(baseURL, apiKey string) *IdentityClient {
	return &IdentityClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
	}
}

type IdentityResponse struct {
	Username     string `json:"username"`
	IdentityType string `json:"identity_type"`
	TenantID     string `json:"tenant_id"`
	Status       string `json:"status"`
}

func (c *IdentityClient) CreateIdentity(ctx context.Context, username, identityType, tenantID string) (*IdentityResponse, error) {
	return &IdentityResponse{
		Username:     username,
		IdentityType: identityType,
		TenantID:     tenantID,
		Status:       "ACTIVE",
	}, nil
}
