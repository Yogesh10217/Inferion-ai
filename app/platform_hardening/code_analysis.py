"""
Platform Code Analysis Engine.
Parses Python files in app/ into AST representations and constructs file, function, class, and import maps.
"""

import ast
import os
from typing import Dict, List, Optional, Tuple


class CodeFileSummary:
    def __init__(self, file_path: str, is_test_file: bool):
        self.file_path = file_path
        self.is_test_file = is_test_file
        self.functions: List[Tuple[str, int, int]] = []  # name, start_line, end_line
        self.classes: List[Tuple[str, int, int]] = []
        self.imports: List[str] = []
        self.ast_tree: Optional[ast.AST] = None
        self.parse_error: Optional[str] = None


class PlatformCodeAnalysisEngine:
    """Scans and parses application source code into AST trees for structural inspection."""

    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir

    def scan_codebase(self) -> Dict[str, CodeFileSummary]:
        summaries: Dict[str, CodeFileSummary] = {}

        if not os.path.exists(self.root_dir):
            return summaries

        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.normpath(os.path.join(root, file))
                    is_test = "tests" in full_path.split(os.sep) or file.startswith("test_")
                    summary = self.analyze_file(full_path, is_test)
                    summaries[full_path] = summary

        return summaries

    def analyze_file(self, file_path: str, is_test: bool = False) -> CodeFileSummary:
        summary = CodeFileSummary(file_path=file_path, is_test_file=is_test)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)
            summary.ast_tree = tree

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    end_line = getattr(node, "end_lineno", node.lineno)
                    summary.functions.append((node.name, node.lineno, end_line))
                elif isinstance(node, ast.ClassDef):
                    end_line = getattr(node, "end_lineno", node.lineno)
                    summary.classes.append((node.name, node.lineno, end_line))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        summary.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        summary.imports.append(f"{module}.{alias.name}")

        except Exception as e:
            summary.parse_error = str(e)

        return summary
