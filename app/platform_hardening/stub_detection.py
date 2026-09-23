"""
Production Stub Detection Engine.
Parses production codebase files with AST analysis to detect and classify stubs.
"""

import ast
import os
from typing import Any, Dict, List

from app.platform_hardening.ast_analysis import ASTNodeFinding, PlatformASTAnalysisEngine
from app.platform_hardening.code_analysis import PlatformCodeAnalysisEngine
from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    StubClassification,
    StubDetectionResult,
)


class ProductionStubDetectionEngine:
    """Scans and classifies stub patterns across production execution paths."""

    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir
        self.code_engine = PlatformCodeAnalysisEngine(root_dir=root_dir)

    def scan_stubs(self, tenant_id: str = "system") -> StubDetectionResult:
        summaries = self.code_engine.scan_codebase()
        findings: List[PlatformAuditFinding] = []
        classifications: Dict[str, int] = {c.value: 0 for c in StubClassification}
        unclassified_stubs_count = 0

        for file_path, summary in summaries.items():
            if summary.parse_error or not summary.ast_tree:
                continue

            ast_engine = PlatformASTAnalysisEngine(file_path=file_path)
            ast_findings = ast_engine.analyze_tree(summary.ast_tree)

            for ast_finding in ast_findings:
                classification = self.classify_finding(file_path, ast_finding, summary.ast_tree)
                classifications[classification.value] += 1

                if classification == StubClassification.PRODUCTION_STUB:
                    unclassified_stubs_count += 1
                    finding = PlatformAuditFinding(
                        finding_id=f"stub-{file_path.replace(os.sep, '_')}-{ast_finding.line_number}",
                        tenant_id=tenant_id,
                        rule_id="RULE-STUB-001",
                        title=f"Production Stub Detected: {ast_finding.name}",
                        description=ast_finding.description,
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=self._extract_subsystem(file_path),
                        affected_component=ast_finding.name,
                        file_path=file_path,
                        line_number=ast_finding.line_number,
                        root_cause_hypothesis="Incomplete implementation or placeholder left in production path.",
                        remediation_suggestion=f"Implement complete production logic for '{ast_finding.name}' or mark as Protocol/ABC.",
                    )
                    findings.append(finding)

        return StubDetectionResult(
            total_files_scanned=len(summaries),
            findings=findings,
            unclassified_stubs_count=unclassified_stubs_count,
            classifications=classifications,
        )

    def classify_finding(self, file_path: str, finding: ASTNodeFinding, tree: Any) -> StubClassification:
        # Check 1: Test path
        norm_path = os.path.normpath(file_path)
        if "tests" in norm_path.split(os.sep) or os.path.basename(file_path).startswith("test_"):
            return StubClassification.TEST_ONLY

        # Check 2: Abstract class / Protocol / Overload
        node = finding.node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                dec_name = ""
                if isinstance(decorator, ast.Name):
                    dec_name = decorator.id
                elif isinstance(decorator, ast.Attribute):
                    dec_name = decorator.attr
                if dec_name in ["abstractmethod", "overload", "runtime_checkable"]:
                    return StubClassification.ABSTRACT

        # Check if parent class inherits from Protocol or ABC
        # If finding.name has a class prefix, check class bases
        if "." in finding.name:
            class_name = finding.name.split(".")[0]
            for stmt in tree.body:
                if isinstance(stmt, ast.ClassDef) and stmt.name == class_name:
                    for base in stmt.bases:
                        base_name = ""
                        if isinstance(base, ast.Name):
                            base_name = base.id
                        elif isinstance(base, ast.Attribute):
                            base_name = base.attr
                        if base_name in ["Protocol", "ABC", "Interface"]:
                            return StubClassification.ABSTRACT

        # Check 3: Optional fallback
        if "optional" in file_path.lower() or "fallback" in file_path.lower():
            return StubClassification.OPTIONAL

        # If none of the above, it's an unclassified PRODUCTION_STUB
        return StubClassification.PRODUCTION_STUB

    def _extract_subsystem(self, file_path: str) -> str:
        parts = os.path.normpath(file_path).split(os.sep)
        if len(parts) >= 2 and parts[0] == "app":
            return parts[1]
        return "app"
