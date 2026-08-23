package llmengine

import (
	"context"
	"net/http"
)

type ArchitectureClient struct {
	client *Client
}

func NewArchitectureClient(c *Client) *ArchitectureClient {
	return &ArchitectureClient{client: c}
}

type CreateNodeRequest struct {
	Name        string                 `json:"name"`
	NodeType    string                 `json:"node_type"`
	Environment string                 `json:"environment,omitempty"`
	Attributes  map[string]interface{} `json:"attributes,omitempty"`
}

type ArchitectureNode struct {
	NodeID     string                 `json:"node_id"`
	TenantID   string                 `json:"tenant_id"`
	Name       string                 `json:"name"`
	NodeType   string                 `json:"node_type"`
	Status     string                 `json:"status"`
	Attributes map[string]interface{} `json:"attributes,omitempty"`
}

func (a *ArchitectureClient) CreateNode(ctx context.Context, req CreateNodeRequest) (*ArchitectureNode, error) {
	var resp ArchitectureNode
	err := a.client.do(ctx, http.MethodPost, "/v1/architecture/nodes", req, &resp)
	if err != nil {
		return nil, err
	}
	return &resp, nil
}

func (a *ArchitectureClient) GetTopology(ctx context.Context, env string) (map[string]interface{}, error) {
	var resp map[string]interface{}
	err := a.client.do(ctx, http.MethodGet, "/v1/architecture/topology?environment="+env, nil, &resp)
	if err != nil {
		return nil, err
	}
	return resp, nil
}
