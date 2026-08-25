// Package llmengine provides the Go SDK for Enterprise AI Reliability Platform (Phase 5.31).
package llmengine

import (
	"context"
	"fmt"
)

type ReliabilityClient struct {
	client *Client
}

type ReliabilityService struct {
	ServiceID string `json:"service_id"`
	TenantID  string `json:"tenant_id"`
	Name      string `json:"name"`
	Tier      string `json:"tier"`
	Status    string `json:"status"`
}

func (c *ReliabilityClient) RegisterService(ctx context.Context, tenantID, name, tier string) (*ReliabilityService, error) {
	path := fmt.Sprintf("/v1/reliability/services?tenant_id=%s", tenantID)
	req := map[string]string{"name": name, "tier": tier}
	var res ReliabilityService
	err := c.client.post(ctx, path, req, &res)
	return &res, err
}
