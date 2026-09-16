"""
Dead Code Detection Engine.
Performs AST call graph & route analysis to detect abandoned code without false deletions.
"""

import ast
import os
from typing import Dict, List, Set, Tuple

from app.platform_hardening.code_analysis import PlatformCodeAnalysisEngine
from app.platform_hardening.models import (
    DeadCodeClassification,
    DeadCodeDetectionResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class DeadCodeDetectionEngine:
    """Analyzes AST call graphs, FastAPI route mappings, and CLI registrations for dead code."""

    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir
        self.code_engine = PlatformCodeAnalysisEngine(root_dir=root_dir)

    def scan_dead_code(self, tenant_id: str = "system") -> DeadCodeDetectionResult:
        summaries = self.code_engine.scan_codebase()
        defined_symbols: Dict[str, Tuple[str, int]] = {}  # symbol_name -> (file_path, line_no)
        referenced_symbols: Set[str] = set()
        route_or_cli_symbols: Set[str] = set()

        # Step 1: Collect definitions and references
        for file_path, summary in summaries.items():
            if summary.parse_error or not summary.ast_tree:
                continue

            # Collect function & class names
            for name, start_line, _ in summary.functions:
                if not name.startswith("_"):  # Focus on non-private symbols
                    defined_symbols[name] = (file_path, start_line)

            for name, start_line, _ in summary.classes:
                defined_symbols[name] = (file_path, start_line)

            # Collect references in AST
            for node in ast.walk(summary.ast_tree):
                if isinstance(node, ast.Name):
                    referenced_symbols.add(node.id)
                elif isinstance(node, ast.Attribute):
                    referenced_symbols.add(node.attr)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        referenced_symbols.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        referenced_symbols.add(node.func.attr)

            # Detect FastAPI route handlers or CLI command registrations
            if "api" in file_path or "cli" in file_path or "main.py" in file_path:
                for name, _, _ in summary.functions:
                    route_or_cli_symbols.add(name)

        # Step 2: Classify dead code candidates
        findings: List[PlatformAuditFinding] = []
        classifications: Dict[str, int] = {c.value: 0 for c in DeadCodeClassification}

        for symbol, (file_path, line_no) in defined_symbols.items():
            classification = self.classify_symbol(
                symbol, file_path, referenced_symbols, route_or_cli_symbols
            )
            classifications[classification.value] += 1

            if classification in [DeadCodeClassification.CONFIRMED_DEAD, DeadCodeClassification.LIKELY_DEAD]:
                finding = PlatformAuditFinding(
                    finding_id=f"dead-{symbol}-{line_no}",
                    tenant_id=tenant_id,
                    rule_id="RULE-DEAD-001",
                    title=f"Potential Dead Code: '{symbol}'",
                    description=f"Symbol '{symbol}' classified as {classification.value}",
                    severity=PlatformAuditSeverity.MEDIUM,
                    subsystem=self._extract_subsystem(file_path),
                    affected_component=symbol,
                    file_path=file_path,
                    line_number=line_no,
                    root_cause_hypothesis="Unreferenced function or class abandoned during architectural refactoring.",
                    remediation_suggestion=f"Verify if '{symbol}' is required or safely delete.",
                )
                findings.append(finding)

        return DeadCodeDetectionResult(
            total_symbols_analyzed=len(defined_symbols),
            findings=findings,
            classifications=classifications,
        )

    def classify_symbol(
        self,
        symbol: str,
        file_path: str,
        referenced_symbols: Set[str],
        route_or_cli_symbols: Set[str],
    ) -> DeadCodeClassification:
        if symbol in route_or_cli_symbols:
            return DeadCodeClassification.DYNAMICALLY_REFERENCED

        if "provider" in file_path.lower() or "manager" in file_path.lower() or "container" in file_path.lower():
            return DeadCodeClassification.DYNAMICALLY_REFERENCED

        if symbol in referenced_symbols:
            return DeadCodeClassification.DYNAMICALLY_REFERENCED

        norm_path = os.path.normpath(file_path)
        if "tests" in norm_path.split(os.sep) or os.path.basename(file_path).startswith("test_"):
            return DeadCodeClassification.TEST_ONLY

        # If not referenced anywhere in codebase
        return DeadCodeClassification.LIKELY_DEAD

    def _extract_subsystem(self, file_path: str) -> str:
        parts = os.path.normpath(file_path).split(os.sep)
        if len(parts) >= 2 and parts[0] == "app":
            return parts[1]
        return "app"
