import os

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

def write_file(rel_path, content):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- 1. PYTHON SDK ---

write_file("sdk/python/pyproject.toml", """
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "llm-engine-sdk"
version = "1.0.0"
description = "Official Python SDK for LLM Inference Engine"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
""")

write_file("sdk/python/llm_engine/__init__.py", """
from .client import LLMEngineClient, AsyncLLMEngineClient
from .auth import APIKeyAuth, BearerAuth
from .exceptions import (
    SDKError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    APIError,
)
from .models import ChatCompletionRequest, ChatCompletionResponse, ModelInfo

__all__ = [
    "LLMEngineClient",
    "AsyncLLMEngineClient",
    "APIKeyAuth",
    "BearerAuth",
    "SDKError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "APIError",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ModelInfo",
]
""")

write_file("sdk/python/llm_engine/exceptions.py", """
class SDKError(Exception):
    pass

class AuthenticationError(SDKError):
    pass

class RateLimitError(SDKError):
    pass

class TimeoutError(SDKError):
    pass

class APIError(SDKError):
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
""")

write_file("sdk/python/llm_engine/auth.py", """
from typing import Dict

class AuthProvider:
    def get_headers(self) -> Dict[str, str]:
        return {}

class APIKeyAuth(AuthProvider):
    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def get_headers(self) -> Dict[str, str]:
        return {self.header_name: self.api_key}

class BearerAuth(AuthProvider):
    def __init__(self, token: str):
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
""")

write_file("sdk/python/llm_engine/models.py", """
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = "stop"

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[UsageInfo] = None

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "llm-engine"
""")

write_file("sdk/python/llm_engine/streaming.py", """
from typing import AsyncGenerator
import json

async def stream_sse_responses(response) -> AsyncGenerator[dict, None]:
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                yield json.loads(data_str)
            except Exception:
                pass
""")

write_file("sdk/python/llm_engine/client.py", """
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from .auth import AuthProvider, APIKeyAuth, BearerAuth
from .exceptions import APIError, AuthenticationError, RateLimitError, TimeoutError
from .models import ChatCompletionRequest, ChatCompletionResponse, ModelInfo
from .streaming import stream_sse_responses

class LLMEngineClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        organization_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        headers = {"Content-Type": "application/json"}
        if organization_id:
            headers["X-Organization-ID"] = organization_id
            
        if auth_provider:
            headers.update(auth_provider.get_headers())
        elif api_key:
            headers.update(APIKeyAuth(api_key).get_headers())

        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=self.timeout)

    def health(self) -> dict:
        res = self.client.get("/health")
        return res.json()

    def list_models(self) -> List[ModelInfo]:
        res = self.client.get("/v1/models")
        data = res.json()
        models_raw = data.get("data", []) if isinstance(data, dict) else data
        return [ModelInfo(**m) for m in models_raw]

    def create_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        res = self.client.post("/v1/chat/completions", json=request.model_dump())
        if res.status_code == 401:
            raise AuthenticationError("Invalid API key or credentials")
        elif res.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif res.status_code >= 400:
            raise APIError(f"API request failed with status {res.status_code}", status_code=res.status_code)
        return ChatCompletionResponse(**res.json())

class AsyncLLMEngineClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        organization_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        headers = {"Content-Type": "application/json"}
        if organization_id:
            headers["X-Organization-ID"] = organization_id
            
        if auth_provider:
            headers.update(auth_provider.get_headers())
        elif api_key:
            headers.update(APIKeyAuth(api_key).get_headers())

        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)

    async def health(self) -> dict:
        res = await self.client.get("/health")
        return res.json()

    async def create_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        res = await self.client.post("/v1/chat/completions", json=request.model_dump())
        if res.status_code == 401:
            raise AuthenticationError("Invalid API key or credentials")
        elif res.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif res.status_code >= 400:
            raise APIError(f"API request failed with status {res.status_code}", status_code=res.status_code)
        return ChatCompletionResponse(**res.json())

    async def stream_chat_completion(self, request: ChatCompletionRequest) -> AsyncGenerator[dict, None]:
        req_data = request.model_dump()
        req_data["stream"] = True
        async with self.client.stream("POST", "/v1/chat/completions", json=req_data) as response:
            async for chunk in stream_sse_responses(response):
                yield chunk

    async def close(self):
        await self.client.aclose()
""")

# Python Examples & Tests
write_file("sdk/python/examples/chat_completion.py", """
from llm_engine import LLMEngineClient, ChatCompletionRequest

client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
req = ChatCompletionRequest(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello LLM Gateway!"}]
)
print("Requesting chat completion...")
# response = client.create_chat_completion(req)
print("Chat completion example ready.")
""")

write_file("sdk/python/examples/streaming.py", """
import asyncio
from llm_engine import AsyncLLMEngineClient, ChatCompletionRequest

async def main():
    client = AsyncLLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "Stream test"}])
    print("Streaming example ready.")
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
""")

write_file("sdk/python/tests/test_client.py", """
import pytest
from llm_engine import LLMEngineClient, ChatCompletionRequest, APIKeyAuth

def test_client_init():
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="my_secret_key")
    assert client.base_url == "http://localhost:8000"
    assert client.client.headers["X-API-Key"] == "my_secret_key"

def test_request_model():
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "test"}])
    assert req.model == "gpt-4"
    assert req.messages[0].role == "user"
""")

# --- 2. TYPESCRIPT SDK ---

write_file("sdk/typescript/package.json", """
{
  "name": "@llm-engine/sdk",
  "version": "1.0.0",
  "description": "Official TypeScript/JavaScript SDK for LLM Inference Engine",
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "echo 'Build TypeScript SDK'",
    "test": "node --test"
  },
  "keywords": ["llm", "ai", "sdk", "typescript"],
  "author": "AGY Team",
  "license": "MIT"
}
""")

write_file("sdk/typescript/tsconfig.json", """
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
""")

write_file("sdk/typescript/src/models.ts", """
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: Message[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface ChatChoice {
  index: number;
  message: Message;
  finish_reason?: string;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatChoice[];
}
""")

write_file("sdk/typescript/src/errors.ts", """
export class SDKError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SDKError';
  }
}

export class AuthenticationError extends SDKError {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends SDKError {
  constructor(message: string = 'Rate limit exceeded') {
    super(message);
    this.name = 'RateLimitError';
  }
}
""")

write_file("sdk/typescript/src/auth.ts", """
export interface AuthHeaders {
  [key: string]: string;
}

export class APIKeyAuth {
  constructor(private apiKey: string, private headerName: string = 'X-API-Key') {}

  getHeaders(): AuthHeaders {
    return { [this.headerName]: this.apiKey };
  }
}
""")

write_file("sdk/typescript/src/client.ts", """
import { ChatCompletionRequest, ChatCompletionResponse } from './models.js';
import { APIKeyAuth } from './auth.js';
import { AuthenticationError, RateLimitError, SDKError } from './errors.js';

export interface ClientConfig {
  baseUrl?: string;
  apiKey?: string;
  organizationId?: string;
  timeoutMs?: number;
}

export class LLMEngineClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: ClientConfig) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\\/+$/, '');
    this.headers = { 'Content-Type': 'application/json' };

    if (config.organizationId) {
      this.headers['X-Organization-ID'] = config.organizationId;
    }
    if (config.apiKey) {
      Object.assign(this.headers, new APIKeyAuth(config.apiKey).getHeaders());
    }
  }

  async health(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/health`, { headers: this.headers });
    return res.json();
  }

  async createChatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    const res = await fetch(`${this.baseUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (res.status === 401) throw new AuthenticationError();
    if (res.status === 429) throw new RateLimitError();
    if (!res.ok) throw new SDKError(`API Error ${res.status}`);

    return res.json() as Promise<ChatCompletionResponse>;
  }
}
""")

write_file("sdk/typescript/src/index.ts", """
export * from './client.js';
export * from './models.js';
export * from './errors.js';
export * from './auth.js';
""")

write_file("sdk/typescript/examples/chat_completion.ts", """
import { LLMEngineClient } from '../src/index.js';

const client = new LLMEngineClient({ baseUrl: 'http://localhost:8000', apiKey: 'test_key' });
console.log('TypeScript SDK initialized');
""")

write_file("sdk/typescript/tests/client.test.ts", """
import { LLMEngineClient } from '../src/index.js';
import assert from 'node:assert';

const client = new LLMEngineClient({ baseUrl: 'http://localhost:8000', apiKey: 'test_key' });
assert.ok(client, 'Client should be instantiated');
console.log('TypeScript SDK tests passed.');
""")

# --- 3. GO SDK ---

write_file("sdk/go/go.mod", """
module github.com/llm-engine/sdk-go

go 1.21
""")

write_file("sdk/go/models.go", """
package llmengine

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatCompletionRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float64   `json:"temperature,omitempty"`
	Stream      bool      `json:"stream,omitempty"`
}

type ChatChoice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason,omitempty"`
}

type ChatCompletionResponse struct {
	ID      string       `json:"id"`
	Object  string       `json:"object"`
	Created int64        `json:"created"`
	Model   string       `json:"model"`
	Choices []ChatChoice `json:"choices"`
}
""")

write_file("sdk/go/errors.go", """
package llmengine

import "fmt"

type SDKError struct {
	StatusCode int
	Message    string
}

func (e *SDKError) Error() string {
	return fmt.Sprintf("SDKError %d: %s", e.StatusCode, e.Message)
}
""")

write_file("sdk/go/client.go", """
package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Config struct {
	BaseURL        string
	APIKey         string
	OrganizationID string
	Timeout        time.Duration
}

type Client struct {
	baseURL string
	apiKey  string
	orgID   string
	hc      *http.Client
}

func NewClient(cfg Config) *Client {
	if cfg.BaseURL == "" {
		cfg.BaseURL = "http://localhost:8000"
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 30 * time.Second
	}
	return &Client{
		baseURL: cfg.BaseURL,
		apiKey:  cfg.APIKey,
		orgID:   cfg.OrganizationID,
		hc:      &http.Client{Timeout: cfg.Timeout},
	}
}

func (c *Client) Health(ctx context.Context) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/health", nil)
	if err != nil {
		return nil, err
	}
	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(res.Body).Decode(&result)
	return result, err
}

func (c *Client) CreateChatCompletion(ctx context.Context, body ChatCompletionRequest) (*ChatCompletionResponse, error) {
	buf, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/v1/chat/completions", bytes.NewReader(buf))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}
	if c.orgID != "" {
		req.Header.Set("X-Organization-ID", c.orgID)
	}

	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode >= 400 {
		return nil, fmt.Errorf("request failed with status: %d", res.StatusCode)
	}

	var resp ChatCompletionResponse
	err = json.NewDecoder(res.Body).Decode(&resp)
	return &resp, err
}
""")

write_file("sdk/go/examples/chat_completion.go", """
package main

import (
	"fmt"
	"github.com/llm-engine/sdk-go"
)

func main() {
	client := llmengine.NewClient(llmengine.Config{
		BaseURL: "http://localhost:8000",
		APIKey:  "test_key",
	})
	fmt.Printf("Go SDK client initialized: %v\\n", client)
}
""")

write_file("sdk/go/tests/client_test.go", """
package tests

import (
	"testing"
	"github.com/llm-engine/sdk-go"
)

func TestNewClient(t *testing.T) {
	client := llmengine.NewClient(llmengine.Config{
		BaseURL: "http://localhost:8000",
		APIKey:  "my_api_key",
	})
	if client == nil {
		t.Fatal("Expected non-nil client")
	}
}
""")

# --- 4. CI/CD WORKFLOW UPDATE ---

write_file(".github/workflows/sdk-publish.yml", """
name: SDK Build and Publish
on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'

jobs:
  build-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Test Python SDK
        run: |
          cd sdk/python
          pip install -e .
          pytest tests/

  build-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Test TypeScript SDK
        run: |
          cd sdk/typescript
          npm test

  build-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Test Go SDK
        run: |
          cd sdk/go
          go test ./...
""")

# --- 5. DOCUMENTATION ---

write_file("docs/sdk.md", """
# Official LLM Engine SDKs (Phase 4.1)

The **LLM Inference Engine** provides official SDKs for Python, TypeScript, and Go.

---

## Python SDK

### Installation
```bash
pip install llm-engine-sdk
```

### Quick Start
```python
from llm_engine import LLMEngineClient, ChatCompletionRequest

client = LLMEngineClient(base_url="http://localhost:8000", api_key="your_api_key")

response = client.create_chat_completion(
    ChatCompletionRequest(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello LLM Engine!"}]
    )
)
print(response.choices[0].message.content)
```

---

## TypeScript SDK

### Installation
```bash
npm install @llm-engine/sdk
```

### Quick Start
```typescript
import { LLMEngineClient } from '@llm-engine/sdk';

const client = new LLMEngineClient({ baseUrl: 'http://localhost:8000', apiKey: 'your_api_key' });

const response = await client.createChatCompletion({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello TypeScript!' }]
});
```

---

## Go SDK

### Installation
```bash
go get github.com/llm-engine/sdk-go
```

### Quick Start
```go
package main

import (
    "context"
    "fmt"
    "github.com/llm-engine/sdk-go"
)

func main() {
    client := llmengine.NewClient(llmengine.Config{
        BaseURL: "http://localhost:8000",
        APIKey:  "your_api_key",
    })

    resp, err := client.CreateChatCompletion(context.Background(), llmengine.ChatCompletionRequest{
        Model: "gpt-4",
        Messages: []llmengine.Message{{Role: "user", Content: "Hello Go!"}},
    })
    if err == nil {
        fmt.Println(resp.Choices[0].Message.Content)
    }
}
```
""")

# --- 6. SDK INTEGRATION TEST ---

write_file("tests/test_sdks.py", """
import pytest
from sdk.python.llm_engine import LLMEngineClient, ChatCompletionRequest

def test_python_sdk_import_and_models():
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "SDK Test"}])
    assert client.base_url == "http://localhost:8000"
    assert req.model == "gpt-4"
""")

print("Phase 4.1 SDK assets generated successfully.")
