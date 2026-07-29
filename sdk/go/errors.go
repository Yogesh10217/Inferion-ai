package llmengine

import "fmt"

type SDKError struct {
	StatusCode int
	Message    string
}

func (e *SDKError) Error() string {
	return fmt.Sprintf("SDKError %d: %s", e.StatusCode, e.Message)
}
