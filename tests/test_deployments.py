import os
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELM_DIR = os.path.join(PROJECT_ROOT, "deploy", "helm", "llm-engine")


def test_helm_chart_yaml_exists():
    chart_path = os.path.join(HELM_DIR, "Chart.yaml")
    assert os.path.exists(chart_path)
    with open(chart_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["name"] == "llm-engine"


def test_helm_values_yaml_valid():
    values_path = os.path.join(HELM_DIR, "values.yaml")
    assert os.path.exists(values_path)
    with open(values_path, "r", encoding="utf-8") as f:
        values = yaml.safe_load(f)
    assert values["securityContext"]["runAsNonRoot"] is True
    assert values["containerSecurityContext"]["readOnlyRootFilesystem"] is True
    assert values["gateway"]["replicaCount"] >= 1


def test_all_helm_templates_exist():
    templates_dir = os.path.join(HELM_DIR, "templates")
    expected_templates = [
        "gateway-deployment.yaml",
        "scheduler-deployment.yaml",
        "service.yaml",
        "ingress.yaml",
        "configmap.yaml",
        "secret.yaml",
        "hpa.yaml",
        "pdb.yaml",
        "networkpolicy.yaml",
        "serviceaccount.yaml",
        "rbac.yaml",
        "pvc.yaml",
        "priorityclass.yaml",
        "servicemonitor.yaml",
        "podmonitor.yaml",
        "prometheusrule.yaml",
    ]
    for tmpl in expected_templates:
        assert os.path.exists(os.path.join(templates_dir, tmpl))
