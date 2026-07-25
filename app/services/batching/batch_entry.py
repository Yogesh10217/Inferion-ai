import time
from dataclasses import dataclass, field
from typing import List

from app.services.request_scheduler import QueueEntry


@dataclass(frozen=True)
class BatchKey:
    provider_id: str
    model_id: str
    stream: bool


@dataclass
class Batch:
    key: BatchKey
    entries: List[QueueEntry] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def size(self) -> int:
        return len(self.entries)

    def add_entry(self, entry: QueueEntry) -> None:
        self.entries.append(entry)

    def elapsed_ms(self) -> float:
        return (time.time() - self.created_at) * 1000
