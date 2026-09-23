"""
Citation Engine Module.
Ensures every answer contains source document, chunk id, page, confidence, and similarity.
"""

import math
from typing import Any, Dict, List

from .reranker import DocumentInfo


class Citation:
    def __init__(
        self,
        doc_id: str,
        chunk_id: str,
        page: int,
        source: str,
        similarity: float,
        confidence_score: float,
        text_snippet: str,
    ):
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.page = page
        self.source = source
        self.similarity = similarity
        self.confidence_score = confidence_score
        self.text_snippet = text_snippet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "page": self.page,
            "source": self.source,
            "similarity": self.similarity,
            "confidence_score": self.confidence_score,
            "text_snippet": self.text_snippet,
        }


class CitationEngine:
    """Manages citations for retrieved contexts."""

    def _calculate_confidence(self, similarity: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
        """
        Calculates a mathematically sound confidence score using a sigmoid function
        centered around a threshold, scaled to [0, 1].
        Assumes similarity is roughly bounded or scales it.
        """
        if max_score > min_score:
            normalized = (similarity - min_score) / (max_score - min_score)
        else:
            normalized = similarity

        # Sigmoid centered at 0.5, steepness 10
        k = 10
        x0 = 0.5
        try:
            confidence = 1 / (1 + math.exp(-k * (normalized - x0)))
        except OverflowError:
            confidence = 0.0 if normalized < x0 else 1.0

        return round(confidence, 4)

    def generate_citations(self, documents: List[DocumentInfo]) -> List[Citation]:
        """
        Extracts citation metadata from retrieved documents.

        Args:
            documents: List of retrieved DocumentInfo objects.

        Returns:
            List[Citation]: List of citations.
        """
        if not documents:
            return []

        scores = [doc.score for doc in documents]
        min_score = min(scores)
        max_score = max(scores)

        citations = []
        for doc in documents:
            meta = doc.metadata or {}

            raw_page = meta.get("page", 1)
            try:
                page = int(raw_page)
            except (ValueError, TypeError):
                page = 1

            confidence = self._calculate_confidence(doc.score, min_score, max_score)

            snippet_length = 150
            snippet = doc.text.strip().replace("\n", " ")
            text_snippet = snippet[:snippet_length] + "..." if len(snippet) > snippet_length else snippet

            citations.append(
                Citation(
                    doc_id=meta.get("doc_id", "unknown_doc"),
                    chunk_id=doc.id,
                    page=page,
                    source=meta.get("source", meta.get("filename", "unknown_source")),
                    similarity=doc.score,
                    confidence_score=confidence,
                    text_snippet=text_snippet,
                )
            )
        return citations

    def format_inline_citations(self, text: str, citations: List[Citation]) -> str:
        """
        Formats text with inline citations referencing the generated citations.
        E.g. Replaces [1] with detailed markdown links or footnotes.
        """
        if not citations:
            return text

        bibliography = "\n\n### Sources\n"
        for i, cit in enumerate(citations):
            bibliography += f"[{i + 1}] {cit.source}, Page {cit.page} (Confidence: {cit.confidence_score:.2f})\n"

        return text + bibliography
