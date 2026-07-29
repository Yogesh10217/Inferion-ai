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
