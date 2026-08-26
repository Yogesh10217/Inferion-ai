// Package llmengine provides the Go SDK for Enterprise AI Knowledge Intelligence Platform (Phase 5.35).
package llmengine

import (
	"context"
	"fmt"
)

type KnowledgeClient struct {
	client *Client
}

type KnowledgeItem struct {
	ItemID         string `json:"item_id"`
	TenantID       string `json:"tenant_id"`
	KnowledgeType  string `json:"knowledge_type"`
	Classification string `json:"classification"`
}

func (c *KnowledgeClient) CreateItem(ctx context.Context, tenantID, title, knowledgeType, classification string) (*KnowledgeItem, error) {
	path := fmt.Sprintf("/v1/knowledge/items?tenant_id=%s", tenantID)
	req := map[string]interface{}{
		"title":          title,
		"knowledge_type": knowledgeType,
		"classification": classification,
	}
	var res KnowledgeItem
	err := c.client.post(ctx, path, req, &res)
	return &res, err
}
