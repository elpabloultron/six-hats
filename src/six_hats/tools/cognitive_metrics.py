"""Cálculo de Complejidad Cognitiva (SonarSource) e Índice de Mantenibilidad (Radon/SEI).

Mide la carga mental de comprensión humana (Sombrero Rojo) y telemetría objetiva
de mantenibilidad de software (Sombrero Blanco).
"""

import ast
import math
from typing import Dict, Any, List, Tuple


class CognitiveComplexityVisitor(ast.NodeVisitor):
    """Calcula la Complejidad Cognitiva según la especificación de SonarSource.

    A diferencia de la complejidad ciclomática de McCabe (que cuenta caminos matemáticos independientes),
    la complejidad cognitiva penaliza fuertemente el anidamiento y la ruptura del flujo secuencial de lectura.
    """

    def __init__(self):
        self.cognitive_complexity = 0
        self._nesting_level = 0

    def _increment(self, penalty: int = 1, apply_nesting: bool = True):
        addition = penalty + (self._nesting_level if apply_nesting else 0)
        self.cognitive_complexity += addition

    def visit_If(self, node: ast.If):
        self._increment(1, apply_nesting=True)
        self._nesting_level += 1
        for item in node.body:
            self.visit(item)
        self._nesting_level -= 1

        # Orelses (elif o else)
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # Es un 'elif': incrementa 1 sin penalización de anidamiento extra
                self._increment(1, apply_nesting=False)
                self.visit(node.orelse[0])
            else:
                # Es un 'else': incrementa 1 sin penalización de anidamiento
                self._increment(1, apply_nesting=False)
                self._nesting_level += 1
                for item in node.orelse:
                    self.visit(item)
                self._nesting_level -= 1

    def visit_For(self, node: ast.For):
        self._increment(1, apply_nesting=True)
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._increment(1, apply_nesting=True)
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_While(self, node: ast.While):
        self._increment(1, apply_nesting=True)
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self._increment(1, apply_nesting=True)
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_BoolOp(self, node: ast.BoolOp):
        # Cada operador lógico en una cadena agrega 1 punto de complejidad cognitiva
        self.cognitive_complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp):
        # Operador ternario: a if b else c
        self._increment(1, apply_nesting=True)
        self.generic_visit(node)


def calculate_cognitive_complexity(code_content: str) -> int:
    """Calcula la puntuación de complejidad cognitiva de SonarSource sobre el código Python."""
    try:
        tree = ast.parse(code_content)
        visitor = CognitiveComplexityVisitor()
        visitor.visit(tree)
        return visitor.cognitive_complexity
    except SyntaxError:
        # Estimación heurística si no es Python válido o es diff
        indent_levels = [len(line) - len(line.lstrip()) for line in code_content.splitlines() if line.strip()]
        avg_indent = sum(indent_levels) / max(1, len(indent_levels))
        branch_count = len([w for w in code_content.split() if w in ("if", "for", "while", "except", "&&", "||")])
        return max(1, int(branch_count * (1 + avg_indent / 4)))


def calculate_maintainability_index(code_content: str, cyclomatic_complexity: int) -> float:
    """Calcula el Índice de Mantenibilidad estándar (0 a 100) según la fórmula del SEI / Radon."""
    lines = [l for l in code_content.splitlines() if l.strip() and not l.strip().startswith("#")]
    sloc = max(1, len(lines))

    # Estimación de volumen de Halstead simplificado
    tokens = code_content.split()
    total_tokens = max(1, len(tokens))
    unique_tokens = max(1, len(set(tokens)))
    halstead_volume = max(1.0, total_tokens * math.log2(unique_tokens + 1))

    # Fórmula del Software Engineering Institute (SEI) normalizada
    raw_mi = 171.0 - (5.2 * math.log(halstead_volume)) - (0.23 * cyclomatic_complexity) - (16.2 * math.log(sloc))
    normalized_mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
    return round(normalized_mi, 1)
