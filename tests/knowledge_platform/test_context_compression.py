"""Unit tests for ContextCompressor token reduction."""

import pytest
from app.knowledge_platform.context import ContextWindow
from app.knowledge_platform.compression import ContextCompressor, CompressionStrategy


def test_context_compression_token_savings():
    compressor = ContextCompressor()
    cwin = ContextWindow(assembled_context="Line 1\nLine 1\nLine 2", token_count=100, tenant_id="t_cmp")

    res = compressor.compress_context(cwin, strategy=CompressionStrategy.DEDUPLICATION, target_ratio=0.5)
    assert res.compressed_tokens == 50
    assert res.tokens_saved == 50
    assert res.provenance_preserved is True
