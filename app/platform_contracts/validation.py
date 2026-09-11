"""Automated Circular Dependency & Contract Architecture Validator (Phase 5.30)."""

import sys
import os
import ast
import logging
from typing import Dict, Any, List, Set

from app.platform_contracts.exceptions import CircularDependencyException

logger = logging.getLogger(__name__)


class DependencyGraph:
    """Represents a module dependency graph and checks for cycles."""

    def __init__(self) -> None:
        self.adj: Dict[str, Set[str]] = {}

    def add_edge(self, u: str, v: str) -> None:
        if u not in self.adj:
            self.adj[u] = set()
        self.adj[u].add(v)

    def detect_cycles(self) -> List[List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle found!
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)

        for node in list(self.adj.keys()):
            if node not in visited:
                dfs(node)

        return cycles


class CircularDependencyValidator:
    """Validates that app/platform_contracts has ZERO domain manager imports."""

    PROHIBITED_IMPORTS = {
        "DataGovernanceManager",
        "ArchitecturePlatformManager",
        "CompliancePlatformManager",
        "PortfolioPlatformManager",
        "DecisionIntelligenceManager",
        "EnterpriseIntelligenceManager",
        "PlatformOperationsManager",
        "ApplicationPlatformManager",
        "DeveloperPlatformManager",
        "AgentOrchestrationManager",
        "PlatformResilienceManager",
        "ControlAssuranceManager",
        "AccessIntelligenceManager",
        "IntegrationIntelligenceManager",
        "OperationsIntelligenceManager",
        "FinOpsIntelligenceManager",
        "DataIntelligenceManager",
        "ModelIntelligenceManager",
        "DecisionGovernanceManager",
        "KnowledgeAssuranceManager",
        "IdentityAssuranceManager",
        "OperationsAssuranceManager",
        "SecurityAssuranceManager",
        "UnifiedIntelligenceManager",
        "AutonomousAssuranceManager",
        "ContinuousAssuranceManager",
        "ReliabilityIntelligenceManager",
        "RuntimeIntelligenceManager",
        "CapacityIntelligenceManager",
        "PlatformIntegrationManager",
        "PlatformHardeningManager",
    }

    PROHIBITED_MODULES = {
        "app.data_governance",
        "app.architecture_platform",
        "app.compliance_platform",
        "app.portfolio_platform",
        "app.decision_intelligence",
        "app.agent_orchestration",
        "app.platform_resilience",
        "app.control_assurance",
        "app.access_intelligence",
        "app.integration_intelligence",
        "app.operations_intelligence",
        "app.finops_intelligence",
        "app.data_intelligence",
        "app.model_intelligence",
        "app.decision_governance",
        "app.knowledge_assurance",
        "app.identity_assurance",
        "app.operations_assurance",
        "app.security_assurance",
        "app.unified_intelligence",
        "app.autonomous_assurance",
        "app.continuous_assurance",
        "app.reliability_intelligence",
        "app.runtime_intelligence",
        "app.capacity_intelligence",
        "app.platform_integration",
        "app.platform_hardening",
    }


    @classmethod
    def validate_platform_contracts_isolation(cls, contracts_dir_path: str) -> bool:
        """Inspects app/platform_contracts AST to ensure zero prohibited domain imports."""
        for root, _, files in os.walk(contracts_dir_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=full_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if any(p in alias.name for p in cls.PROHIBITED_MODULES):
                                    raise CircularDependencyException(f"Forbidden import '{alias.name}' in '{full_path}'")
                        elif isinstance(node, ast.ImportFrom):
                            mod = node.module or ""
                            if any(p in mod for p in cls.PROHIBITED_MODULES):
                                raise CircularDependencyException(f"Forbidden import from '{mod}' in '{full_path}'")
                            for alias in node.names:
                                if alias.name in cls.PROHIBITED_IMPORTS:
                                    raise CircularDependencyException(f"Forbidden symbol import '{alias.name}' in '{full_path}'")
        return True


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    contracts_dir = os.path.join(base_dir, "platform_contracts")
    logger.info(f"Validating platform_contracts isolation at: {contracts_dir}")
    try:
        CircularDependencyValidator.validate_platform_contracts_isolation(contracts_dir)
        print("SUCCESS: app/platform_contracts is 100% dependency-light with ZERO domain manager imports.")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
