from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PipelineStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DocumentContext:
    """Context object carrying document data through the pipeline stages."""
    document_id: str
    raw_content: Optional[bytes] = None
    parsed_content: Optional[str] = None
    metadata: Dict[str, Any] = None
    chunks: List[Dict[str, Any]] = None
    embeddings: List[List[float]] = None
    status: PipelineStatus = PipelineStatus.PENDING
    errors: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.chunks is None:
            self.chunks = []
        if self.embeddings is None:
            self.embeddings = []
        if self.errors is None:
            self.errors = []

class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""
    
    @abstractmethod
    async def process(self, context: DocumentContext) -> DocumentContext:
        """Processes the document context."""
        pass
