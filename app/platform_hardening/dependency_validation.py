"""
Platform Dependency Validation Engine.
Constructs module dependency graphs and enforces layer boundary isolation & contract protection.
"""

import os
from typing import Dict, List, Set

from app.platform_hardening.code_analysis import PlatformCodeAnalysisEngine
from app.platform_hardening.models import (
    DependencyValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformDependencyValidationEngine:
    """Validates import dependencies across platform modules and checks for layer violations."""

    PROHIBITED_CONTRACT_IMPORTS = [
        "app.unified_intelligence.manager",
        "app.decision_intelligence.manager",
        "app.autonomous_assurance.manager",
        "app.continuous_assurance.manager",
        "app.reliability_intelligence.manager",
        "app.capacity_intelligence.manager",
        "app.runtime_intelligence.manager",
        "app.platform_integration.manager",
        "app.platform_hardening.manager",
    ]

    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir
        self.code_engine = PlatformCodeAnalysisEngine(root_dir=root_dir)

    def validate_dependencies(self, tenant_id: str = "system") -> DependencyValidationResult:
        summaries = self.code_engine.scan_codebase()
        dep_graph: Dict[str, Set[str]] = {}  # module -> imported_modules
        prohibited_imports_found: List[str] = []
        findings: List[PlatformAuditFinding] = []

        for file_path, summary in summaries.items():
            mod_name = self._file_path_to_module(file_path)
            dep_graph[mod_name] = set()

            for imp in summary.imports:
                dep_graph[mod_name].add(imp)

                # Invariant 3 check: Check if app/platform_contracts/ imports any domain manager directly
                if "platform_contracts" in file_path:
                    for prohibited in self.PROHIBITED_CONTRACT_IMPORTS:
                        if prohibited in imp:
                            prohibited_imports_found.append(f"{file_path} imports {imp}")
                            findings.append(
                                PlatformAuditFinding(
                                    finding_id=f"dep-violation-{mod_name}",
                                    tenant_id=tenant_id,
                                    rule_id="RULE-DEP-001",
                                    title=f"Platform Contract Import Violation: '{imp}'",
                                    description=f"File '{file_path}' directly imports domain manager '{imp}' violating Provider Decoupling Invariant 3.",
                                    severity=PlatformAuditSeverity.CRITICAL,
                                    subsystem="platform_contracts",
                                    affected_component=file_path,
                                    file_path=file_path,
                                    root_cause_hypothesis="Direct domain manager import breaks platform contract isolation.",
                                    remediation_suggestion="Refactor platform_contracts to interact via Provider Protocols and Registries.",
                                )
                            )

        # Detect circular dependencies in graph
        cycles = self._find_cycles(dep_graph)
        for cycle in cycles:
            findings.append(
                PlatformAuditFinding(
                    finding_id=f"cycle-{'->'.join(cycle[:3])}",
                    tenant_id=tenant_id,
                    rule_id="RULE-DEP-002",
                    title="Circular Dependency Detected",
                    description=f"Circular dependency cycle: {' -> '.join(cycle)}",
                    severity=PlatformAuditSeverity.HIGH,
                    subsystem="platform",
                    affected_component=cycle[0],
                    root_cause_hypothesis="Tight coupling between subsystems created an import loop.",
                    remediation_suggestion="Decouple subsystem interfaces using abstract protocols or dependency injection.",
                )
            )

        is_valid = len(prohibited_imports_found) == 0 and len(cycles) == 0

        return DependencyValidationResult(
            is_valid=is_valid,
            circular_dependencies=cycles,
            prohibited_imports=prohibited_imports_found,
            findings=findings,
        )

    def _file_path_to_module(self, file_path: str) -> str:
        rel = os.path.relpath(file_path, ".")
        rel = rel.replace(".py", "").replace(os.sep, ".")
        return rel

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        cycles = []
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            stack.append(node)

            for neighbor in graph.get(node, []):
                # Only check internal app module dependencies
                if neighbor.startswith("app."):
                    if neighbor in stack:
                        idx = stack.index(neighbor)
                        cycles.append(stack[idx:] + [neighbor])
                    elif neighbor not in visited:
                        dfs(neighbor)

            stack.pop()

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node)

        return cycles[:10]  # Limit cycle list length
