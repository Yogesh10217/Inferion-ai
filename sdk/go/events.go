// Package llmengine provides the Go SDK for Enterprise AI Event Intelligence Platform (Phase 5.34).
package llmengine

import (
	"context"
	"fmt"
)

type EventsClient struct {
	client *Client
}

type EnterpriseEvent struct {
	EventID   string `json:"event_id"`
	TenantID  string `json:"tenant_id"`
	EventType string `json:"event_type"`
	Severity  string `json:"severity"`
}

func (c *EventsClient) Create(ctx context.Context, tenantID, sourceName, eventType, category, severity string, payload map[string]interface{}) (*EnterpriseEvent, error) {
	path := fmt.Sprintf("/v1/events?tenant_id=%s", tenantID)
	req := map[string]interface{}{
		"source_name": sourceName,
		"event_type":  eventType,
		"category":    category,
		"severity":    severity,
		"payload":     payload,
	}
	var res EnterpriseEvent
	err := c.client.post(ctx, path, req, &res)
	return &res, err
}
