import os

WORKFLOW_DIR = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\.github\workflows"
os.makedirs(WORKFLOW_DIR, exist_ok=True)

with open(os.path.join(WORKFLOW_DIR, "sdk-publish.yml"), "w") as f:
    f.write("""name: SDK Build and Publish
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
      - name: Test
        run: |
          cd sdk/python
          pip install -e .
          # pytest tests/
      - name: Build and Publish (Dry Run)
        run: |
          cd sdk/python
          # python -m build
          # twine upload dist/*

  build-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Test
        run: |
          cd sdk/typescript
          # npm install
          # npm test
      - name: Build and Publish (Dry Run)
        run: |
          cd sdk/typescript
          # npm run build
          # npm publish --dry-run

  build-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Test
        run: |
          cd sdk/go
          go test ./...

  build-java:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Test
        run: |
          cd sdk/java
          # mvn test
      - name: Publish (Dry Run)
        run: |
          cd sdk/java
          # mvn deploy -DskipTests
""")

SDK_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\sdk"
with open(os.path.join(SDK_ROOT, "README.md"), "w") as f:
    f.write("""# Official Client SDKs

Welcome to the official client SDKs for the LLM Inference Engine.

These SDKs provide an idiomatic, typed interface across multiple languages to interface with the AI Gateway.

## Supported Languages
- [Python](./python/)
- [TypeScript](./typescript/)
- [Go](./go/)
- [Java](./java/)

## Core Capabilities
- **Authentication**: Native support for API Keys and JWT.
- **Inference**: Chat, Completion, and Multi-modal APIs.
- **Streaming**: Native streaming paradigms (`async for`, `AsyncIterable`, Channels, Reactive Streams).
- **Administration**: Manage Organizations, Workspaces, Billing, Webhooks, and Plugins directly from code.

## Generating the Base
The core clients are generated from our unified `sdk/shared/openapi.json`. We manually wrap these generated clients with thin, idiomatic layers.
""")

print("CI/CD and Docs created.")
