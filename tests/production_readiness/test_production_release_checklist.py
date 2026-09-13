from __future__ import annotations

import pytest
from app.deployment.models import ProductionReleaseDecision
from app.deployment.production_release_checklist import ProductionReleaseChecklistEvaluator


def test_production_release_checklist_sections():
    res = ProductionReleaseChecklistEvaluator.evaluate_checklist()

    assert res.total_sections == 14
    assert res.decision in (ProductionReleaseDecision.GO, ProductionReleaseDecision.MANUAL_REVIEW_REQUIRED)


def test_production_release_checklist_failure():
    res = ProductionReleaseChecklistEvaluator.evaluate_checklist({"artifact_valid": False})

    assert res.decision == ProductionReleaseDecision.NO_GO
    assert res.failed_sections >= 1
