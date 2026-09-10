# Official LLM Engine SDKs (Phase 4.1)

The **Inferion AI** provides official SDKs for Python, TypeScript, and Go.

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
