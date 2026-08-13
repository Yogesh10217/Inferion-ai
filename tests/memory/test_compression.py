"""
Tests for Memory Compressor Engine
"""

from app.memory.memory_compressor import MemoryCompressor


def test_memory_compressor_deduplication():
    compressor = MemoryCompressor()
    facts = ["Fact 1", "Fact 2", "Fact 1", "FACT 1 ", "Fact 3"]
    deduped = compressor.deduplicate_facts(facts)

    assert len(deduped) == 3
    assert deduped == ["Fact 1", "Fact 2", "Fact 3"]


def test_memory_compressor_messages():
    compressor = MemoryCompressor()
    msgs = [{"role": "user", "content": f"msg {i}"} for i in range(10)]
    res = compressor.compress_messages(msgs)

    assert res["compressed_count"] == 5
    assert len(res["messages"]) == 5
