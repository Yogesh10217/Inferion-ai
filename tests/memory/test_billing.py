"""
Tests for Memory Usage & Billing Operations Tracking
"""

from app.memory.memory_manager import MemoryManager


def test_memory_billing_ops_tracking():
    mm = MemoryManager()
    mm.create_memory("Billing tracking memory entry 1", organization_id="org_bill")
    mm.create_memory("Billing tracking memory entry 2", organization_id="org_bill")
    mm.search_memories("Billing", organization_id="org_bill")

    analytics = mm.get_analytics()
    assert analytics["total_writes"] == 2
    assert analytics["total_searches"] == 1
