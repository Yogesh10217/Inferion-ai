"""Unit tests for Application Composition Engine."""

from app.application_platform.composition import (
    ApplicationCompositionManager,
    ComponentType,
)


def test_create_and_validate_composition():
    comp_mgr = ApplicationCompositionManager()
    comp = comp_mgr.create_composition(
        application_id="app_100",
        tenant_id="t1",
        name="Support Copilot Composition",
    )

    cmp1 = comp_mgr.add_component(
        composition_id=comp.composition_id,
        name="Knowledge Base",
        component_type=ComponentType.KNOWLEDGE_SOURCE,
        resource_id="kb_support_v2",
        sequence_order=1,
    )

    comp_mgr.add_component(
        composition_id=comp.composition_id,
        name="Support Agent",
        component_type=ComponentType.AGENT,
        resource_id="agent_tier1",
        sequence_order=2,
        depends_on=[cmp1.component_id],
    )

    validation = comp_mgr.validate_composition(comp.composition_id)
    assert validation["valid"] is True
    assert validation["component_count"] == 2
