"""
Platform Duplication Detection Engine.
Detects duplicate models, enums, normalizers, and exception classes across phase directories.
"""

import ast
import os
from typing import Dict, List, Tuple
from app.platform_hardening.code_analysis import PlatformCodeAnalysisEngine
from app.platform_hardening.models import (
    DuplicateDetectionResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformDuplicationDetectionEngine:
    """Scans phase modules for duplicate contract schemas, enums, and lifecycle states."""

    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir
        self.code_engine = PlatformCodeAnalysisEngine(root_dir=root_dir)

    def scan_duplicates(self, tenant_id: str = "system") -> DuplicateDetectionResult:
        summaries = self.code_engine.scan_codebase()
        class_declarations: Dict[str, List[Tuple[str, int]]] = {}

        for file_path, summary in summaries.items():
            if summary.parse_error or not summary.ast_tree:
                continue

            for class_name, line_no, _ in summary.classes:
                if class_name not in class_declarations:
                    class_declarations[class_name] = []
                class_declarations[class_name].append((file_path, line_no))

        findings: List[PlatformAuditFinding] = []
        duplicates_count = 0

        # Filter out common base class names like "Base", "Config"
        ignored_names = {"Base", "Config", "Settings", "Meta"}

        for class_name, locations in class_declarations.items():
            if class_name in ignored_names:
                continue

            if len(locations) > 1:
                # Discovered duplicate class definition across files
                subsystems = {self._extract_subsystem(loc[0]) for loc in locations}
                if len(subsystems) > 1:  # Duplicated across different subsystem domains
                    duplicates_count += 1
                    loc_desc = ", ".join([f"{loc[0]}:L{loc[1]}" for loc in locations])
                    finding = PlatformAuditFinding(
                        finding_id=f"dup-{class_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-DUP-001",
                        title=f"Duplicate Contract Definition: '{class_name}'",
                        description=f"Class '{class_name}' defined in multiple subsystems ({loc_desc})",
                        severity=PlatformAuditSeverity.HIGH if "Status" in class_name or "State" in class_name else PlatformAuditSeverity.MEDIUM,
                        subsystem="app",
                        affected_component=class_name,
                        file_path=locations[0][0],
                        line_number=locations[0][1],
                        root_cause_hypothesis="Subsystem decoupled development resulted in redundant duplicate model definitions.",
                        remediation_suggestion=f"Consolidate '{class_name}' into app/platform_contracts or shared model module.",
                    )
                    findings.append(finding)

        return DuplicateDetectionResult(
            duplicates_found=duplicates_count,
            findings=findings,
        )

    def _extract_subsystem(self, file_path: str) -> str:
        parts = os.path.normpath(file_path).split(os.sep)
        if len(parts) >= 2 and parts[0] == "app":
            return parts[1]
        return "app"
