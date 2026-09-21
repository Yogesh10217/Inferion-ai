"""Unit tests for PromptManager and PromptOps."""

from app.mlops.prompt_management import PromptManager
from app.mlops.registry import AIAssetRegistry


def test_prompt_rendering_and_versioning():
    registry = AIAssetRegistry()
    prompt_mgr = PromptManager(registry=registry)

    p_id = prompt_mgr.create_prompt(
        name="Support Greeting",
        template_str="Hello {customer_name}, how can I help you with {product}?",
        input_variables=["customer_name", "product"],
    )

    rendered = prompt_mgr.render_template(p_id, "1.0.0", {"customer_name": "Alice", "product": "Enterprise Cloud"})
    assert rendered == "Hello Alice, how can I help you with Enterprise Cloud?"
