package llmengine
type Client struct {
    APIKey  string
    BaseURL string
}
func NewClient(apiKey string) *Client {
    return &Client{APIKey: apiKey}
}
