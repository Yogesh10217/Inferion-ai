import pytest

from app.knowledge.pipeline import DocumentContext
from app.knowledge.pipeline_runner import PipelineRunner


@pytest.mark.asyncio
async def test_pipeline_runner_init():
    runner = PipelineRunner(stages=[])
    assert runner.stages == []
    ctx = DocumentContext(document_id="doc1")
    res = await runner.run(ctx)
    assert res.document_id == "doc1"
