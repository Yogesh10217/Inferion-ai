"""
Unified Memory Coordinator
"""

from typing import Optional

from app.agents.memory.conversation import ConversationMemory
from app.agents.memory.store import IMemoryStore, InMemoryStore
from app.agents.memory.working import WorkingMemory


class MemoryCoordinator:
    def __init__(self, store: Optional[IMemoryStore] = None):
        self.store = store or InMemoryStore()
        self.working_memory = WorkingMemory()
        self.conversation_memory = ConversationMemory()

    async def save_session_memory(self, session_id: str) -> None:
        data = {
            "working_memory": self.working_memory.model_dump(),
            "conversation_messages": [m.model_dump() for m in self.conversation_memory.messages],
            "conversation_summary": self.conversation_memory.summary
        }
        await self.store.set(f"memory:{session_id}", data)

    async def load_session_memory(self, session_id: str) -> bool:
        data = await self.store.get(f"memory:{session_id}")
        if not data:
            return False
        self.working_memory = WorkingMemory(**data["working_memory"])
        self.conversation_memory.summary = data.get("conversation_summary")
        return True
