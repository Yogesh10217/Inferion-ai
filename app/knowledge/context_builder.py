"""
Context Builder Module.
Assembles context for the LLM (ordering chunks, removing duplicates, semantic deduplication, adjacent chunk merging, token budgeting, prompt formatting).
"""

import difflib
import logging
from typing import List, Optional, Tuple

from .citation_engine import Citation, CitationEngine
from .reranker import DocumentInfo

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds optimized context for LLM consumption."""

    def __init__(
        self,
        max_tokens: int = 4000,
        citation_engine: Optional[CitationEngine] = None,
        similarity_threshold: float = 0.85,
    ):
        self.max_tokens = max_tokens
        self.citation_engine = citation_engine or CitationEngine()
        self.similarity_threshold = similarity_threshold

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (approx 4 chars per token). Could use tiktoken if installed."""
        return len(text) // 4

    def _semantic_deduplicate(self, documents: List[DocumentInfo]) -> List[DocumentInfo]:
        """Removes exact duplicates and semantically similar chunks (e.g. overlapping content)."""
        unique_docs = []
        for doc in documents:
            is_duplicate = False
            for existing in unique_docs:
                if doc.id == existing.id:
                    is_duplicate = True
                    break
                # Check text similarity
                matcher = difflib.SequenceMatcher(None, doc.text, existing.text)
                if matcher.ratio() > self.similarity_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_docs.append(doc)
        return unique_docs

    def _merge_adjacent_chunks(self, documents: List[DocumentInfo]) -> List[DocumentInfo]:
        """Merge chunks that are adjacent in the original document to provide continuous context."""
        if not documents:
            return []

        # Group by document ID (assuming source doc ID is in metadata)
        # Sort primarily by source doc ID, secondarily by chunk index/page
        def sort_key(doc):
            source_id = doc.metadata.get("doc_id", "")
            chunk_idx = doc.metadata.get("chunk_index", 0)
            return (source_id, chunk_idx)

        docs_sorted = sorted(documents, key=sort_key)
        merged_docs = []

        current_doc = docs_sorted[0]

        for next_doc in docs_sorted[1:]:
            curr_source = current_doc.metadata.get("doc_id")
            next_source = next_doc.metadata.get("doc_id")

            curr_idx = current_doc.metadata.get("chunk_index", -1)
            next_idx = next_doc.metadata.get("chunk_index", -2)

            # If same source and adjacent chunk
            if curr_source and curr_source == next_source and next_idx == curr_idx + 1:
                # Merge
                merged_text = current_doc.text + "\n" + next_doc.text
                current_doc.text = merged_text
                current_doc.metadata["chunk_index"] = next_idx  # Update to last index
                # Update score to max
                current_doc.score = max(current_doc.score, next_doc.score)
            else:
                merged_docs.append(current_doc)
                current_doc = next_doc

        merged_docs.append(current_doc)

        # Restore original relevance ordering based on max score
        return sorted(merged_docs, key=lambda x: x.score, reverse=True)

    def build_context(self, documents: List[DocumentInfo]) -> Tuple[str, List[Citation]]:
        """
        Assembles document chunks into a single context string within token budgets.

        Args:
            documents: List of retrieved documents.

        Returns:
            Tuple containing the formatted context string and the list of citations.
        """
        import time

        from app.monitoring.metrics import knowledge_context_build_seconds, knowledge_errors_total

        start_time = time.time()

        try:
            # 1. Deduplicate
            unique_docs = self._semantic_deduplicate(documents)

            # 2. Merge adjacent
            merged_docs = self._merge_adjacent_chunks(unique_docs)

            context_parts = []
            current_tokens = 0
            accepted_docs = []

            for idx, doc in enumerate(merged_docs):
                source = doc.metadata.get("source", doc.metadata.get("doc_id", "Unknown"))
                page = doc.metadata.get("page", "Unknown")

                # Prompt formatting
                chunk_text = f"--- Document {idx + 1} ---\nSource: {source} (Page: {page})\nConfidence: {doc.score:.2f}\nContent:\n{doc.text}\n"
                chunk_tokens = self._estimate_tokens(chunk_text)

                if current_tokens + chunk_tokens > self.max_tokens:
                    logger.warning(f"Token limit ({self.max_tokens}) reached. Truncated at document {idx}")
                    break

                context_parts.append(chunk_text)
                current_tokens += chunk_tokens
                accepted_docs.append(doc)

            final_context = "\n".join(context_parts)
            citations = self.citation_engine.generate_citations(accepted_docs)

            return final_context, citations
        except Exception:
            knowledge_errors_total.inc()
            raise
        finally:
            knowledge_context_build_seconds.observe(time.time() - start_time)
