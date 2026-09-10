import ast
import re
from typing import List, Tuple
from six_hats.core.models import WhiteHatData


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """Calcula la complejidad ciclomática de McCabe recorriendo los nodos del AST."""

    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.complexity += len(node.ifs)
        self.generic_visit(node)


def extract_ast_from_python(code: str) -> Tuple[List[str], int, List[str]]:
    """Extrae símbolos, complejidad ciclomática e imports de código Python válido."""
    tree = ast.parse(code)
    
    symbols: List[str] = []
    dependencies: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            symbols.append(f"def {node.name}")
        elif isinstance(node, ast.AsyncFunctionDef):
            symbols.append(f"async def {node.name}")
        elif isinstance(node, ast.ClassDef):
            symbols.append(f"class {node.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.append(node.module)

    visitor = CyclomaticComplexityVisitor()
    visitor.visit(tree)

    return symbols, visitor.complexity, sorted(list(set(dependencies)))


def extract_heuristics(code: str) -> Tuple[List[str], int, List[str]]:
    """Extracción heurística para diffs o código de otros lenguajes de programación."""
    symbols = []
    # Buscar patrones comunes de funciones o clases
    patterns = [
        r"(?:def|class|function|fn|interface|struct)\s+([A-Za-z0-9_]+)",
        r"(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:function|\()",
    ]
    for p in patterns:
        for m in re.finditer(p, code):
            symbols.append(m.group(0))

    # Estimación de complejidad ciclomática mediante palabras clave de bifurcación
    branch_keywords = ["if", "else", "for", "while", "case", "catch", "switch", "&&", "||"]
    complexity = 1
    for kw in branch_keywords:
        complexity += len(re.findall(r"\b" + re.escape(kw) + r"\b", code))

    # Imports comunes
    import_patterns = [
        r"(?:import|from)\s+([A-Za-z0-9_\.]+)",
        r"require\(['\"]([^'\"]+)['\"]\)",
        r"#include\s+[<'\"]([^>'\"]+)[>'\"]",
    ]
    deps = []
    for p in import_patterns:
        for m in re.finditer(p, code):
            deps.append(m.group(1))

    return symbols, max(1, complexity), sorted(list(set(deps)))


from six_hats.tools.cognitive_metrics import (
    calculate_cognitive_complexity,
    calculate_maintainability_index,
)


from six_hats.tools.tree_sitter_engine import analyze_tree_sitter


def extract_ast_data(
    code_content: str, lines_added: int = 0, lines_deleted: int = 0, filename: str = "source.py"
) -> WhiteHatData:
    """Procesa el contenido del código o diff y construye el modelo de datos de Sombrero Blanco."""
    symbols: List[str] = []
    complexity = 1
    cognitive_comp = 0
    deps: List[str] = []

    # 1. Intentar análisis con Tree-sitter si no es Python o si Tree-sitter está disponible
    ts_result = analyze_tree_sitter(code_content, filename=filename)
    if ts_result is not None:
        symbols, complexity, cognitive_comp, deps = ts_result
    else:
        # 2. Fallback al analizador de AST de Python o heurística
        try:
            symbols, complexity, deps = extract_ast_from_python(code_content)
            cognitive_comp = calculate_cognitive_complexity(code_content)
        except SyntaxError:
            symbols, complexity, deps = extract_heuristics(code_content)
            cognitive_comp = calculate_cognitive_complexity(code_content)

    lines = code_content.splitlines()
    total_lines = len(lines)
    if lines_added == 0 and lines_deleted == 0:
        lines_added = total_lines

    maintainability = calculate_maintainability_index(code_content, complexity)

    # 3. Métricas de Git Churn (pydriller) y Cobertura real
    from six_hats.tools.git_utils import analyze_git_churn, detect_coverage_report
    churn_desc, hist_risk = analyze_git_churn(filename)
    coverage_rate = detect_coverage_report(filename)
    cov_summary = f"{coverage_rate} % de líneas cubiertas" if coverage_rate is not None else None

    return WhiteHatData(
        symbols_affected=symbols,
        cyclomatic_complexity=complexity,
        cognitive_complexity=cognitive_comp,
        maintainability_index=maintainability,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
        test_coverage_pct=coverage_rate or 0.0,
        dependencies=deps,
        git_churn_score=churn_desc,
        historical_risk=hist_risk,
        coverage_summary=cov_summary,
    )


