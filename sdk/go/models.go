package llmengine

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ModelsService struct {
	client *Client
}

func (s *ModelsService) ListModels() (map[string]interface{}, error) {
	resp, err := http.Get(fmt.Sprintf("%s/v1/models", s.client.BaseURL))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}
