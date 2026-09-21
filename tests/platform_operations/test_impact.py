"""Unit tests for Operational Impact & Blast Radius Analyzer."""

from app.platform_operations.impact import ImpactAnalyzer, ImpactLevel
from app.platform_operations.services import ServiceCatalogManager, ServiceTier


def test_impact_analysis_for_critical_tier_service():
    svc_mgr = ServiceCatalogManager()
    s1 = svc_mgr.register_service("t1", "Payment Service", service_tier=ServiceTier.TIER_0_CRITICAL)
    s2 = svc_mgr.register_service("t1", "Checkout App")

    svc_mgr.add_dependency("t1", source_service_id=s2.service_id, target_service_id=s1.service_id)

    analyzer = ImpactAnalyzer(service_catalog_manager=svc_mgr)
    assessment = analyzer.assess_impact("t1", s1.service_id)

    assert assessment.impact_level == ImpactLevel.CRITICAL
    assert assessment.estimated_blast_radius_score > 0.3
    assert s1.service_id in assessment.affected_services
