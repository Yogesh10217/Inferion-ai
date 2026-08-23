package llmengine

import (
	"context"
	"fmt"
)

type DataGovernanceClient struct {
	client *Client
}

type DataAsset struct {
	AssetID        string `json:"asset_id"`
	TenantID       string `json:"tenant_id"`
	Name           string `json:"name"`
	Type           string `json:"type"`
	Classification string `json:"classification"`
}

func (c *DataGovernanceClient) ListAssets(ctx context.Context, tenantID string) ([]DataAsset, error) {
	var resp struct {
		Assets []DataAsset `json:"assets"`
	}
	err := c.client.get(ctx, fmt.Sprintf("/v1/data-governance/assets?tenant_id=%s", tenantID), &resp)
	if err != nil {
		return nil, err
	}
	return resp.Assets, nil
}
