"""Unit tests for TimeoutManager."""

import asyncio

import pytest

from app.resilience.timeout import TimeoutException, TimeoutManager, TimeoutPolicy


@pytest.mark.asyncio
async def test_timeout_enforcement():
    tm = TimeoutManager(TimeoutPolicy(tool_timeout_seconds=0.1))

    async def slow_tool():
        await asyncio.sleep(0.5)

    with pytest.raises(TimeoutException):
        await tm.execute_with_timeout("tool", slow_tool)
