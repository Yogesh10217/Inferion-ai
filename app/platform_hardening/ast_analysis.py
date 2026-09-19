"""
Platform AST Analysis Engine.
Inspects AST nodes for stub patterns, pass statements, constant returns, and manager bypasses.
"""

import ast
from typing import Any, Dict, List, Optional


class ASTNodeFinding:
    def __init__(
        self,
        finding_type: str,
        name: str,
        line_number: int,
        description: str,
        node: ast.AST,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.finding_type = finding_type  # PASS_ONLY, NOT_IMPLEMENTED, EMPTY_RETURN, CONSTANT_RETURN, MANAGER_BYPASS
        self.name = name
        self.line_number = line_number
        self.description = description
        self.node = node
        self.details = details or {}


class PlatformASTAnalysisEngine(ast.NodeVisitor):
    """AST visitor searching Python syntax trees for stub patterns and architectural anomalies."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.findings: List[ASTNodeFinding] = []
        self._current_class: Optional[str] = None
        self._current_func: Optional[str] = None

    def analyze_tree(self, tree: ast.AST) -> List[ASTNodeFinding]:
        self.findings.clear()
        self.visit(tree)
        return self.findings

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_function(node)

    def _check_function(self, node: Any):
        prev_func = self._current_func
        func_name = f"{self._current_class}.{node.name}" if self._current_class else node.name
        self._current_func = func_name

        # Strip docstrings from body for stub evaluation
        body_stmts = [
            s
            for s in node.body
            if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
        ]

        # 1. Pass-only function
        if len(body_stmts) == 1 and isinstance(body_stmts[0], ast.Pass):
            self.findings.append(
                ASTNodeFinding(
                    finding_type="PASS_ONLY",
                    name=func_name,
                    line_number=node.lineno,
                    description=f"Function '{func_name}' body contains only 'pass'",
                    node=node,
                )
            )

        # 2. Raise NotImplementedError
        elif len(body_stmts) == 1 and isinstance(body_stmts[0], ast.Raise):
            exc = body_stmts[0].exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id in ["NotImplementedError", "NotImplemented"]:
                    self.findings.append(
                        ASTNodeFinding(
                            finding_type="NOT_IMPLEMENTED",
                            name=func_name,
                            line_number=node.lineno,
                            description=f"Function '{func_name}' raises {exc.func.id}",
                            node=node,
                        )
                    )
            elif isinstance(exc, ast.Name) and exc.id in ["NotImplementedError", "NotImplemented"]:
                self.findings.append(
                    ASTNodeFinding(
                        finding_type="NOT_IMPLEMENTED",
                        name=func_name,
                        line_number=node.lineno,
                        description=f"Function '{func_name}' raises {exc.id}",
                        node=node,
                    )
                )

        # 3. Empty return / dummy return
        elif len(body_stmts) == 1 and isinstance(body_stmts[0], ast.Return):
            ret_val = body_stmts[0].value
            if ret_val is None:
                self.findings.append(
                    ASTNodeFinding(
                        finding_type="EMPTY_RETURN",
                        name=func_name,
                        line_number=node.lineno,
                        description=f"Function '{func_name}' returns None implicitly or explicitly",
                        node=node,
                    )
                )
            elif isinstance(ret_val, ast.Dict) and len(ret_val.keys) == 0:
                self.findings.append(
                    ASTNodeFinding(
                        finding_type="EMPTY_RETURN",
                        name=func_name,
                        line_number=node.lineno,
                        description=f"Function '{func_name}' returns empty dict {{}}",
                        node=node,
                    )
                )
            elif isinstance(ret_val, ast.List) and len(ret_val.elts) == 0:
                self.findings.append(
                    ASTNodeFinding(
                        finding_type="EMPTY_RETURN",
                        name=func_name,
                        line_number=node.lineno,
                        description=f"Function '{func_name}' returns empty list []",
                        node=node,
                    )
                )
            elif isinstance(ret_val, ast.Dict):
                # Check for constant return dicts like {"status": "success", "score": 100}
                if all(
                    isinstance(k, ast.Constant) and isinstance(v, ast.Constant)
                    for k, v in zip(ret_val.keys, ret_val.values)
                ):
                    self.findings.append(
                        ASTNodeFinding(
                            finding_type="CONSTANT_RETURN",
                            name=func_name,
                            line_number=node.lineno,
                            description=f"Function '{func_name}' returns a hardcoded static dictionary",
                            node=node,
                        )
                    )

        # 4. Check for Manager bypass (Manager class directly invoking _repository or _db method instead of engine)
        if self._current_class and "Manager" in self._current_class:
            for stmt in node.body:
                for child in ast.walk(stmt):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                        attr = child.func
                        if isinstance(attr.value, ast.Attribute) and "repo" in attr.value.attr.lower():
                            self.findings.append(
                                ASTNodeFinding(
                                    finding_type="MANAGER_BYPASS",
                                    name=func_name,
                                    line_number=child.lineno,
                                    description=f"Manager '{self._current_class}' directly calls repository method '{attr.attr}' bypassing engines",
                                    node=child,
                                )
                            )

        self.generic_visit(node)
        self._current_func = prev_func
