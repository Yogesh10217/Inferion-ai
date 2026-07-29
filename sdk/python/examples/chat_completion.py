from llm_engine import LLMEngineClient, ChatCompletionRequest

client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
req = ChatCompletionRequest(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello LLM Gateway!"}]
)
print("Requesting chat completion...")
# response = client.create_chat_completion(req)
print("Chat completion example ready.")
