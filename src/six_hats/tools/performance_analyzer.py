"""Analizador estático de rendimiento y complejidad asintótica Big-O para el Sombrero Amarillo.

Detecta trampas algorítmicas O(n²), operaciones ineficientes en bucles y oportunidades
de vectorización y modernización sintáctica.
"""

import ast
from typing import List, Dict, Any


class PerformanceAstVisitor(ast.NodeVisitor):
    """Inspección de AST para detectar trampas de rendimiento algorítmico."""

    def __init__(self):
        self.loop_depth = 0
        self.bottlenecks: List[Dict[str, str]] = []

    def visit_For(self, node: ast.For):
        self.loop_depth += 1
        # Detección de bucles anidados directos O(n²)
        for child in node.body:
            if isinstance(child, (ast.For, ast.While)):
                self.bottlenecks.append(
                    {
                        "type": "Bucles Anidados O(n² / n×m)",
                        "location": f"Línea {node.lineno}",
                        "description": "Bucle for anidado directamente. La complejidad algorítmica escala cuadráticamente con el tamaño de los datos.",
                        "remediation": "Utilizar estructuras de indexación previa (dict/hash map), joins en memoria o procesamiento en lote vectorizado.",
                    }
                )
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node: ast.Call):
        # 1. Detección de list.pop(0)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "pop":
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
                is_in_loop = self.loop_depth > 0
                comp = "O(n²)" if is_in_loop else "O(n)"
                self.bottlenecks.append(
                    {
                        "type": f"list.pop(0) Ineficiente ({comp})",
                        "location": f"Línea {node.lineno}",
                        "description": (
                            f"Llamada a .pop(0) desplaza todos los elementos restantes en memoria con costo O(n). "
                            + ("Al ejecutarse dentro de un bucle, eleva la complejidad a O(n²)." if is_in_loop else "")
                        ),
                        "remediation": "Reemplazar la lista por collections.deque y utilizar .popleft() para costo garantizado O(1).",
                    }
                )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        # 2. Búsqueda lineal 'item in list' dentro de bucles
        if self.loop_depth > 0:
            for op in node.ops:
                if isinstance(op, (ast.In, ast.NotIn)):
                    self.bottlenecks.append(
                        {
                            "type": "Búsqueda Lineal en Bucle O(n²)",
                            "location": f"Línea {node.lineno}",
                            "description": "Operador 'in' evaluado dentro de un bucle sobre una colección no indexada. Costo acumulado O(n × m).",
                            "remediation": "Convertir la colección de búsqueda a un set() o dict() antes de ingresar al bucle para resolución O(1).",
                        }
                    )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        # 3. Concatenación cuadrática de cadenas s += ... en bucle
        if self.loop_depth > 0 and isinstance(node.op, ast.Add):
            if isinstance(node.target, ast.Name):
                self.bottlenecks.append(
                    {
                        "type": "Concatenación de Cadenas en Bucle O(n²)",
                        "location": f"Línea {node.lineno}",
                        "description": "Concatenación iterativa con '+=' dentro de bucle. Cada asignación reasigna memoria y copia el buffer completo.",
                        "remediation": "Acumular fragmentos en una lista y ensamblar al final con ''.join(chunks) en O(n).",
                    }
                )
        self.generic_visit(node)


def analyze_performance_bottlenecks(code_content: str) -> List[Dict[str, str]]:
    """Ejecuta el análisis asintótico Big-O sobre el código fuente."""
    try:
        tree = ast.parse(code_content)
        visitor = PerformanceAstVisitor()
        visitor.visit(tree)
        return visitor.bottlenecks
    except SyntaxError:
        # Heurística textual de respaldo
        bottlenecks: List[Dict[str, str]] = []
        if ".pop(0)" in code_content:
            bottlenecks.append(
                {
                    "type": "list.pop(0) Ineficiente",
                    "location": "Uso de .pop(0)",
                    "description": "Desplazamiento O(n) de elementos en memoria. Reemplazar por deque.popleft().",
                    "remediation": "Usar collections.deque.",
                }
            )
        if " in " in code_content and ("for " in code_content or "while " in code_content):
            bottlenecks.append(
                {
                    "type": "Búsqueda Lineal Potencial en Bucle",
                    "location": "Iteración con búsqueda de pertenencia",
                    "description": "Evaluar si la colección de búsqueda puede pre-hashearse en un conjunto set().",
                    "remediation": "Usar set() para búsquedas O(1).",
                }
            )
        return bottlenecks
