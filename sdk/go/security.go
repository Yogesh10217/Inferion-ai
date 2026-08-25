// Package llmengine provides the Go SDK for Enterprise AI Security Intelligence Platform (Phase 5.32).
package llmengine

import (
	"context"
	"fmt"
)

type SecurityClient struct {
	client *Client
}

type SecurityAsset struct {
	AssetID    string `json:"asset_id"`
	TenantID   string `json:"tenant_id"`
	Name       string `json:"name"`
	AssetType  string `json:"asset_type"`
	Criticality string `json:"criticality"`
}

func (c *SecurityClient) RegisterAsset(ctx context.Context, tenantID, name, assetType, criticality string) (*SecurityAsset, error) {
	path := fmt.Sprintf("/v1/security/assets?tenant_id=%s", tenantID)
	req := map[string]string{"name": name, "asset_type": assetType, "criticality": criticality}
	var res SecurityAsset
	err := c.client.post(ctx, path, req, &res)
	return &res, err
}
