"""Unit tests for TimeoutManager."""

import pytest
import asyncio
from app.resilience.timeout import TimeoutManager, TimeoutPolicy, TimeoutException


@pytest.mark.asyncio
async def test_timeout_enforcement():
    tm = TimeoutManager(TimeoutPolicy(tool_timeout_seconds=0.1))

    async def slow_tool():
        await asyncio.sleep(0.5)

    with pytest.raises(TimeoutException):
        await tm.execute_with_timeout("tool", slow_tool)
