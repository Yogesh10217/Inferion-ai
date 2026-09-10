package llmengine

import (
	"context"
)

type ComplianceClient struct {
	client *Client
}

func NewComplianceClient(client *Client) *ComplianceClient {
	return &ComplianceClient{client: client}
}

func (c *ComplianceClient) AdoptFramework(ctx context.Context, frameworkType, name, description string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"framework_type": frameworkType,
		"name":           name,
		"description":    description,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/compliance/frameworks", payload, &res)
	return res, err
}

func (c *ComplianceClient) ListFrameworks(ctx context.Context) ([]map[string]interface{}, error) {
	var res []map[string]interface{}
	err := c.client.Get(ctx, "/v1/compliance/frameworks", &res)
	return res, err
}

func (c *ComplianceClient) RegisterControl(ctx context.Context, code, name, description, controlType, category string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"code":         code,
		"name":         name,
		"description":  description,
		"control_type": controlType,
		"category":     category,
	}
	var res map[string]interface{}
	err := c.client.Post(ctx, "/v1/compliance/controls", payload, &res)
	return res, err
}

func (c *ComplianceClient) GetPosture(ctx context.Context) (map[string]interface{}, error) {
	var res map[string]interface{}
	err := c.client.Get(ctx, "/v1/compliance/posture", &res)
	return res, err
}
