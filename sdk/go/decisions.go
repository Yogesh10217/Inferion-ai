package llmengine

import (
	"context"
	"fmt"
)

type DecisionsClient struct {
	client *Client
}

func NewDecisionsClient(client *Client) *DecisionsClient {
	return &DecisionsClient{client: client}
}

func (c *DecisionsClient) CreateContext(ctx context.Context, title, description string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"title":       title,
		"description": description,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/decisions/context", payload, &res)
	return res, err
}

func (c *DecisionsClient) Analyze(ctx context.Context, title string) (map[string]interface{}, error) {
	payload := map[string]interface{}{"title": title}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/decisions/analyze", payload, &res)
	return res, err
}

func (c *DecisionsClient) GetDecision(ctx context.Context, decisionID string) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Get(ctx, fmt.Sprintf("/v1/decisions/%s", decisionID), &res)
	return res, err
}

func (c *DecisionsClient) FinalizeDecision(ctx context.Context, decisionID string) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Post(ctx, fmt.Sprintf("/v1/decisions/%s/finalize", decisionID), nil, &res)
	return res, err
}

func (c *DecisionsClient) GetAnalytics(ctx context.Context) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Get(ctx, "/v1/decisions/analytics", &res)
	return res, err
}
