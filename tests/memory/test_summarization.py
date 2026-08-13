"""
Tests for Memory Summarizer Engine
"""

import pytest
from app.memory.memory_summarizer import MemorySummarizer


@pytest.mark.asyncio
async def test_memory_summarizer_text():
    summarizer = MemorySummarizer()
    long_text = " ".join([f"word_{i}" for i in range(150)])
    summary = await summarizer.summarize_text(long_text, max_words=20)

    assert len(summary.split()) == 20
    assert summary.endswith("...")


@pytest.mark.asyncio
async def test_memory_summarizer_run():
    summarizer = MemorySummarizer()
    steps = [{"node_id": "start"}, {"node_id": "agent1"}, {"node_id": "end"}]
    summary = await summarizer.summarize_run("run_123", steps)

    assert "run_123" in summary
    assert "start, agent1, end" in summary
