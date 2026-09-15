package llmengine

import (
	"bufio"
	"encoding/json"
	"io"
	"strings"
)

type ChatCompletionChunk struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	Model   string `json:"model"`
	Choices []struct {
		Index int `json:"index"`
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
		FinishReason *string `json:"finish_reason"`
	} `json:"choices"`
}

type StreamResponse struct {
	Chunk ChatCompletionChunk
	Err   error
}

type Stream struct {
	reader *bufio.Reader
	body   io.ReadCloser
}

func NewStream(body io.ReadCloser) *Stream {
	return &Stream{
		reader: bufio.NewReader(body),
		body:   body,
	}
}

func (s *Stream) Recv() (ChatCompletionChunk, error) {
	for {
		line, err := s.reader.ReadString('\n')
		if err != nil {
			s.body.Close()
			return ChatCompletionChunk{}, err
		}

		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, ":") {
			continue
		}

		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")
			if data == "[DONE]" {
				s.body.Close()
				return ChatCompletionChunk{}, io.EOF
			}

			var chunk ChatCompletionChunk
			if err := json.Unmarshal([]byte(data), &chunk); err != nil {
				continue
			}
			return chunk, nil
		}
	}
}

func (s *Stream) Close() error {
	return s.body.Close()
}
