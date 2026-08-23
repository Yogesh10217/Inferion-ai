"""Python SDK Client for Compliance, Controls & Assurance Platform (Phase 5.27)."""

from typing import Dict, Any, Optional, List


class ComplianceClient:
    """Client for Compliance Platform REST API."""

    def __init__(self, client) -> None:
        self.client = client

    def adopt_framework(self, framework_type: str, name: str, description: str = "Framework") -> Dict[str, Any]:
        """Adopt compliance framework."""
        payload = {
            "framework_type": framework_type,
            "name": name,
            "description": description,
        }
        return self.client._request("POST", "/v1/compliance/frameworks", json=payload)

    def list_frameworks(self) -> List[Dict[str, Any]]:
        """List compliance frameworks."""
        return self.client._request("GET", "/v1/compliance/frameworks")

    def register_control(self, code: str, name: str, description: str, control_type: str = "PREVENTIVE", category: str = "SECURITY") -> Dict[str, Any]:
        """Register compliance control."""
        payload = {
            "code": code,
            "name": name,
            "description": description,
            "control_type": control_type,
            "category": category,
        }
        return self.client._request("POST", "/v1/compliance/controls", json=payload)

    def list_controls(self) -> List[Dict[str, Any]]:
        """List controls."""
        return self.client._request("GET", "/v1/compliance/controls")

    def collect_evidence(self, idempotency_key: str, subject_type: str, subject_id: str, required_types: List[str]) -> Dict[str, Any]:
        """Collect compliance evidence with idempotency."""
        payload = {
            "idempotency_key": idempotency_key,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "required_evidence_types": required_types,
        }
        return self.client._request("POST", "/v1/compliance/evidence/collect", json=payload)

    def run_assessment(self, framework_id: str, subject_id: str = "global") -> Dict[str, Any]:
        """Run compliance assessment."""
        payload = {"framework_id": framework_id, "subject_id": subject_id}
        return self.client._request("POST", "/v1/compliance/assessments", json=payload)

    def get_posture(self) -> Dict[str, Any]:
        """Get tenant compliance posture score."""
        return self.client._request("GET", "/v1/compliance/posture")

    def generate_assurance_report(self, framework_id: str, conclusion: str = "ASSURED") -> Dict[str, Any]:
        """Generate immutable assurance report."""
        payload = {"framework_id": framework_id, "conclusion": conclusion}
        return self.client._request("POST", "/v1/compliance/assurance", json=payload)

    def create_audit_package(self, framework_id: str, evidence_bundle_ref: str, assurance_report_ref: str) -> Dict[str, Any]:
        """Create immutable audit package."""
        payload = {
            "framework_id": framework_id,
            "evidence_bundle_reference": evidence_bundle_ref,
            "assurance_report_reference": assurance_report_ref,
        }
        return self.client._request("POST", "/v1/compliance/audit-packages", json=payload)

    def get_analytics(self) -> Dict[str, Any]:
        """Get compliance analytics report."""
        return self.client._request("GET", "/v1/compliance/analytics")
