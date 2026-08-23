package llmengine

import (
	"context"
)

type PortfolioClient struct {
	client *Client
}

func NewPortfolioClient(client *Client) *PortfolioClient {
	return &PortfolioClient{client: client}
}

func (c *PortfolioClient) CreateStrategy(ctx context.Context, name, description, horizon string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"name":        name,
		"description": description,
		"horizon":     horizon,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/portfolio/strategies", payload, &res)
	return res, err
}

func (c *PortfolioClient) ListStrategies(ctx context.Context) ([]map[string]interface{}, error) {
	var res []map[string]interface{}
	err := c.client.Get(ctx, "/v1/portfolio/strategies", &res)
	return res, err
}

func (c *PortfolioClient) DiscoverOpportunity(ctx context.Context, title, description string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"title":       title,
		"description": description,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/portfolio/opportunities", payload, &res)
	return res, err
}

func (c *PortfolioClient) CreateInitiative(ctx context.Context, title, description string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"title":       title,
		"description": description,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/portfolio/initiatives", payload, &res)
	return res, err
}

func (c *PortfolioClient) Prioritize(ctx context.Context) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/portfolio/prioritize", nil, &res)
	return res, err
}

func (c *PortfolioClient) Optimize(ctx context.Context) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/portfolio/optimize", nil, &res)
	return res, err
}

func (c *PortfolioClient) GetAnalytics(ctx context.Context) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Get(ctx, "/v1/portfolio/analytics", &res)
	return res, err
}
