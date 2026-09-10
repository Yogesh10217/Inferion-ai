"""Runtime impact assessment engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RuntimeImpactAssessmentEngine:
    """Evaluates runtime impact across 10 business and technical dimensions."""

    def evaluate_impact(
        self,
        tenant_id: str,
        component_id: str,
        incident_id: Optional[str] = None,
        affected_components: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        aff = affected_components or [component_id]
        spread_multiplier = min(2.0, 1.0 + (len(aff) * 0.15))

        # Weight dimensions based on component role
        is_security_comp = any(k in component_id.lower() for k in ["sec", "auth", "token", "iam"])
        is_data_comp = any(k in component_id.lower() for k in ["db", "data", "storage", "vector"])
        is_gateway = any(k in component_id.lower() for k in ["gw", "ingress", "api", "router"])

        base_ops = min(1.0, 0.50 * spread_multiplier)
        base_cust = min(1.0, (0.75 if is_gateway else 0.40) * spread_multiplier)
        base_sec = 0.85 if is_security_comp else 0.15
        base_data = 0.80 if is_data_comp else 0.20

        dimensions = {
            "BUSINESS": round(min(1.0, (base_ops + base_cust) / 2.0), 3),
            "SECURITY": round(base_sec, 3),
            "OPERATIONS": round(base_ops, 3),
            "COMPLIANCE": round(0.10 if not is_security_comp else 0.70, 3),
            "FINANCIAL": round(min(1.0, base_ops * 0.7), 3),
            "DATA": round(base_data, 3),
            "MODEL": round(0.40 if "model" in component_id.lower() else 0.20, 3),
            "IDENTITY": round(0.80 if "auth" in component_id.lower() else 0.10, 3),
            "CUSTOMER": round(base_cust, 3),
            "REPUTATION": round(min(1.0, (base_cust + base_sec) / 2.0), 3),
        }
        overall_impact = sum(dimensions.values()) / len(dimensions)

        if overall_impact >= 0.70:
            severity_level = "CRITICAL"
        elif overall_impact >= 0.45:
            severity_level = "HIGH"
        elif overall_impact >= 0.25:
            severity_level = "MEDIUM"
        else:
            severity_level = "LOW"

        logger.info(f"Evaluated RuntimeImpactAssessment for '{component_id}': Overall={overall_impact:.3f} ({severity_level})")
        return {
            "tenant_id": tenant_id,
            "component_id": component_id,
            "incident_id": incident_id,
            "overall_impact": round(overall_impact, 4),
            "severity_level": severity_level,
            "dimensions": dimensions,
            "affected_components": aff,
        }
