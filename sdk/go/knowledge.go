package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type KnowledgeClient struct {
	client *Client
}

func (k *KnowledgeClient) doReq(ctx context.Context, method, path string, body interface{}) (*http.Response, error) {
	var bodyReader *bytes.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewReader(buf)
	} else {
		bodyReader = bytes.NewReader([]byte{})
	}

	req, err := http.NewRequestWithContext(ctx, method, k.client.baseURL+path, bodyReader)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	if k.client.apiKey != "" {
		req.Header.Set("X-API-Key", k.client.apiKey)
	}
	if k.client.orgID != "" {
		req.Header.Set("X-Organization-ID", k.client.orgID)
	}

	res, err := k.client.hc.Do(req)
	if err != nil {
		return nil, err
	}
	if res.StatusCode >= 400 {
		res.Body.Close()
		return nil, fmt.Errorf("request failed with status: %d", res.StatusCode)
	}
	return res, nil
}

func (k *KnowledgeClient) Create(ctx context.Context, name, description string) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "POST", "/v1/knowledge/create", map[string]string{"name": name, "description": description})
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}

func (k *KnowledgeClient) List(ctx context.Context) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "GET", "/v1/knowledge/list", nil)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}

// Additional Go methods...


func (k *KnowledgeClient) Citations(ctx context.Context, query, indexID string) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "POST", "/v1/knowledge/citations", map[string]string{"query": query, "index_id": indexID})
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}
