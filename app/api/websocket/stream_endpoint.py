"""
WebSocket Inference Streaming Endpoint.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter(tags=["websocket"])


@router.websocket("/v1/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """Real-time bi-directional streaming inference over WebSocket."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                model = payload.get("model", "gpt-4o-mini")

                # Stream token chunks back over WebSocket
                tokens = [f"Token-{i} " for i in range(1, 6)]
                for tok in tokens:
                    await websocket.send_json({
                        "object": "chat.completion.chunk",
                        "model": model,
                        "delta": {"content": tok},
                    })
                    await asyncio.sleep(0.05)

                await websocket.send_json({"event": "DONE", "model": model})
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format payload"})
    except WebSocketDisconnect:
        pass
