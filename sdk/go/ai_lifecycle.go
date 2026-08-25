// Package llmengine provides the Go SDK for Enterprise AI Lifecycle Platform (Phase 5.33).
package llmengine

import (
	"context"
	"fmt"
)

type AILifecycleClient struct {
	client *Client
}

type AIAsset struct {
	AssetID   string `json:"asset_id"`
	TenantID  string `json:"tenant_id"`
	Name      string `json:"name"`
	AssetType string `json:"asset_type"`
}

func (c *AILifecycleClient) RegisterAsset(ctx context.Context, tenantID, name, assetType, description string) (*AIAsset, error) {
	path := fmt.Sprintf("/v1/ai-lifecycle/assets?tenant_id=%s", tenantID)
	req := map[string]string{"name": name, "asset_type": assetType, "description": description}
	var res AIAsset
	err := c.client.post(ctx, path, req, &res)
	return &res, err
}
