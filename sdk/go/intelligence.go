package llmengine

import (
	"context"
	"fmt"
)

type IntelligenceClient struct {
	baseURL string
	apiKey  string
}

func NewIntelligenceClient(baseURL string, apiKey string) *IntelligenceClient {
	return &IntelligenceClient{baseURL: baseURL, apiKey: apiKey}
}

func (c *IntelligenceClient) IngestSignal(ctx context.Context, source string, signalType string, message string, tenantID string) (string, error) {
	return fmt.Sprintf("IngestSignal %s/%s for tenant %s from %s", source, signalType, tenantID, c.baseURL), nil
}

func (c *IntelligenceClient) ListRecommendations(ctx context.Context, tenantID string) (string, error) {
	return fmt.Sprintf("ListRecommendations for tenant %s from %s", tenantID, c.baseURL), nil
}
