import asyncio
from llm_engine import AsyncLLMEngineClient, ChatCompletionRequest

async def main():
    client = AsyncLLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "Stream test"}])
    print("Streaming example ready.")
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
