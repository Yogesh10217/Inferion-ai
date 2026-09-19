import hashlib
import re
from enum import Enum
from typing import Dict, List, Tuple

import tiktoken

from app.knowledge.pipeline import DocumentContext, PipelineStage


class ChunkingStrategy(Enum):
    RECURSIVE = "recursive"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    TOKEN_AWARE = "token_aware"  # nosec B105


class ChunkingStage(PipelineStage):
    """Splits parsed content into configurable chunks."""

    def __init__(
        self, strategy: ChunkingStrategy = ChunkingStrategy.TOKEN_AWARE, chunk_size: int = 500, chunk_overlap: int = 50
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _get_block_info(self, offset: int, blocks: List[Dict]) -> Dict:
        for b in blocks:
            if b["start_offset"] <= offset < b["end_offset"]:
                return b
        if blocks:
            return blocks[-1]
        return {"page_number": 1, "section_heading": None}

    def _create_chunk_metadata(
        self, text: str, start_char: int, document_id: str, index: int, blocks: List[Dict]
    ) -> Dict:
        block_info = self._get_block_info(start_char, blocks)
        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)
        end_char = start_char + len(text)
        chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        return {
            "chunk_id": f"{document_id}_chunk_{index}",
            "text": text,
            "strategy": self.strategy.value,
            "page_number": block_info.get("page_number", 1),
            "start_offset": start_char,
            "end_offset": end_char,
            "section_heading": block_info.get("section_heading", None),
            "token_count": token_count,
            "chunk_hash": chunk_hash,
            "parent_chunk": None,
            "version": 1,
        }

    def _split_recursive(self, text: str) -> List[Tuple[str, int]]:
        separators = ["\n\n", "\n", ". ", " ", ""]
        chunks = []

        def split_text(t: str, offset: int):
            if len(t) <= self.chunk_size:
                chunks.append((t, offset))
                return
            for sep in separators:
                if sep in t:
                    splits = t.split(sep)
                    current_chunk = ""
                    current_offset = offset
                    for s in splits:
                        part = s + sep
                        if len(current_chunk) + len(part) > self.chunk_size and current_chunk:
                            chunks.append((current_chunk, current_offset))
                            current_offset += len(current_chunk)
                            current_chunk = part
                        else:
                            current_chunk += part
                    if current_chunk:
                        chunks.append((current_chunk, current_offset))
                    return
            chunks.append((t, offset))

        split_text(text, 0)
        return chunks

    def _split_sentence(self, text: str) -> List[Tuple[str, int]]:
        sentences = re.split(r"(?<=[.!?]) +", text)
        chunks = []
        current_chunk = ""
        current_offset = 0

        for s in sentences:
            if len(current_chunk) + len(s) > self.chunk_size and current_chunk:
                chunks.append((current_chunk, current_offset))
                current_offset += len(current_chunk)
                current_chunk = s + " "
            else:
                current_chunk += s + " "

        if current_chunk:
            chunks.append((current_chunk, current_offset))

        return chunks

    def _split_semantic(self, blocks: List[Dict]) -> List[Tuple[str, int]]:
        chunks = []
        current_chunk = ""
        current_offset = 0

        for b in blocks:
            text = b["text"]
            offset = b["start_offset"]

            if len(current_chunk) + len(text) > self.chunk_size and current_chunk:
                chunks.append((current_chunk, current_offset))
                current_offset = offset
                current_chunk = text
            else:
                if not current_chunk:
                    current_offset = offset
                current_chunk += text

        if current_chunk:
            chunks.append((current_chunk, current_offset))

        return chunks

    def _split_token_aware(self, text: str) -> List[Tuple[str, int]]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        current_char_idx = 0

        for i in range(0, len(tokens), max(1, self.chunk_size - self.chunk_overlap)):
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            start_idx = text.find(chunk_text[:20], current_char_idx)
            if start_idx == -1:
                start_idx = current_char_idx
            else:
                current_char_idx = start_idx + max(1, len(chunk_text) // 2)

            chunks.append((chunk_text, start_idx))

        return chunks

    async def process(self, context: DocumentContext) -> DocumentContext:
        """Chunks the document content."""
        if not context.parsed_content:
            context.errors.append("No parsed content to chunk.")
            return context

        text = context.parsed_content
        blocks = context.metadata.get("blocks", [])

        if self.strategy == ChunkingStrategy.RECURSIVE:
            raw_chunks = self._split_recursive(text)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            raw_chunks = self._split_sentence(text)
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            raw_chunks = self._split_semantic(blocks)
        elif self.strategy == ChunkingStrategy.TOKEN_AWARE:
            raw_chunks = self._split_token_aware(text)
        else:
            raw_chunks = self._split_recursive(text)

        chunks = []
        for i, (chunk_text, offset) in enumerate(raw_chunks):
            chunk_meta = self._create_chunk_metadata(chunk_text, offset, context.document_id, i, blocks)
            chunks.append(chunk_meta)

        context.chunks = chunks
        return context
