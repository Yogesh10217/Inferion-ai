from app.operations.observability_engine import ObservabilityEngine
from app.operations.operational_certification import OperationalCertificationEngine, OperationalCertificationStatus
from app.operations.sli import SLIEvaluator
from app.operations.slo import SLOEvaluator


def test_operational_certification_ready():
    obs = ObservabilityEngine().collect_observations()
    sli = SLIEvaluator().evaluate(obs)
    slo = SLOEvaluator().evaluate(sli)

    cert_engine = OperationalCertificationEngine()
    res = cert_engine.evaluate_certification(
        observation=obs,
        slo_results=slo,
        error_budget_result=None,
        alerts=[],
        incidents=[],
        deployment_health=None,
        evidence=None,
        is_production=False,
    )

    assert res.certification_status == OperationalCertificationStatus.OPERATIONALLY_READY
    assert res.is_certified is True
    assert res.truthfulness_matrix["PRODUCTION_DEPLOYED"] == "NOT_EXECUTED"


def test_operational_certification_production_not_executed():
    obs = ObservabilityEngine().collect_observations()
    sli = SLIEvaluator().evaluate(obs)
    slo = SLOEvaluator().evaluate(sli)

    cert_engine = OperationalCertificationEngine()
    res = cert_engine.evaluate_certification(
        observation=obs,
        slo_results=slo,
        error_budget_result=None,
        alerts=[],
        incidents=[],
        deployment_health=None,
        evidence=None,
        is_production=True,
    )

    assert res.certification_status == OperationalCertificationStatus.NOT_EXECUTED
    assert res.is_certified is False
