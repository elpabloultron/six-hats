"""Motor Ponytail Anti-Sobreingeniería basado en la «Escalera de la Pereza» (Ladder of Laziness).

Audita código para detectar abstracciones innecesarias, reinvenciones de la biblioteca
estándar, código especulativo (YAGNI) y complejidad accidental.
"""

import ast
import re
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("six_hats.ponytail_rules")


class PonytailViolation(BaseModel):
    rung: int = Field(description="Peldaño de la Escalera de la Pereza (1 a 6)")
    name: str = Field(description="Nombre de la regla o principio de pereza infringido")
    severity: str = Field(description="Gravedad: CRITICAL, HIGH, MEDIUM, LOW")
    location: str = Field(description="Línea o símbolo donde ocurre la sobreingeniería")
    description: str = Field(description="Explicación del exceso de código y cómo simplificarlo")
    lazy_recommendation: str = Field(description="Solución mínima y directa recomendada")


class PonytailAuditReport(BaseModel):
    bloat_score: float = Field(description="Índice de sobreingeniería de 0 % (óptimo) a 100 % (hiper-complejo)")
    lines_analyzed: int = Field(description="Total de líneas evaluadas")
    estimated_lines_reducible: int = Field(description="Líneas estimadas que se pueden eliminar")
    violations: List[PonytailViolation] = Field(default_factory=list, description="Violaciones a la Escalera de la Pereza")
    ladder_summary: Dict[str, int] = Field(default_factory=dict, description="Violaciones detectadas por peldaño")
    is_acceptable: bool = Field(description="True si el nivel de sobreingeniería está bajo el umbral tolerable")


class PonytailVisitor(ast.NodeVisitor):
    """Analizador de AST que rastrea sobreingeniería estructural."""

    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.violations: List[PonytailViolation] = []
        self.classes_defined: Dict[str, ast.ClassDef] = {}
        self.functions_defined: Dict[str, ast.FunctionDef] = {}

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes_defined[node.name] = node

        # Peldaño 1: Clases con un único método que podrían ser una función simple
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(methods) == 1 and methods[0].name not in ("__init__", "__repr__", "__str__"):
            self.violations.append(
                PonytailViolation(
                    rung=1,
                    name="Clase de Método Único (Anti-YAGNI)",
                    severity="MEDIUM",
                    location=f"Línea {node.lineno}: class {node.name}",
                    description=f"La clase «{node.name}» solo encapsula el método «{methods[0].name}». No tiene estado interno persistente.",
                    lazy_recommendation=f"Elimina la clase y convierte «{methods[0].name}» en una función directa.",
                )
            )

        # Clases de solo paso (Abstract wrappers sin implementación)
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            if not any(base.id in ("Exception", "BaseException") for base in node.bases if isinstance(base, ast.Name)):
                self.violations.append(
                    PonytailViolation(
                        rung=1,
                        name="Clase Vacía / Abstracción Especulativa",
                        severity="LOW",
                        location=f"Línea {node.lineno}: class {node.name}",
                        description="Clase sin atributos ni métodos que solo contiene «pass».",
                        lazy_recommendation="Aplica YAGNI: borra esta clase hasta que exista una necesidad concreta.",
                    )
                )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions_defined[node.name] = node

        # Peldaño 6: Bucles de acumulación redundantes que caben en una línea idiomática
        if len(node.body) == 3:
            # Patrón común: lista vacía, for loop con append, return lista
            if (
                isinstance(node.body[0], ast.Assign)
                and isinstance(node.body[1], ast.For)
                and isinstance(node.body[2], ast.Return)
            ):
                for_node = node.body[1]
                if len(for_node.body) == 1 and isinstance(for_node.body[0], ast.Expr):
                    call = for_node.body[0].value
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "append":
                        self.violations.append(
                            PonytailViolation(
                                rung=6,
                                name="Bucle Imperativo Verboso",
                                severity="LOW",
                                location=f"Línea {node.lineno}: def {node.name}",
                                description="Bucle for tradicional utilizado únicamente para filtrar/mapear elementos en una lista.",
                                lazy_recommendation="Reemplázalo por una comprensión de lista concisa o expresión generadora en una sola línea.",
                            )
                        )

        # Peldaño 1: Funciones proxy que solo llaman a otra función sin añadir valor
        if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
            ret_val = node.body[0].value
            if isinstance(ret_val, ast.Call) and isinstance(ret_val.func, ast.Name):
                if len(node.args.args) == len(ret_val.args):
                    self.violations.append(
                        PonytailViolation(
                            rung=1,
                            name="Función Wrapper Redundante",
                            severity="MEDIUM",
                            location=f"Línea {node.lineno}: def {node.name}",
                            description=f"La función «{node.name}» es un envoltorio innecesario que solo reenvía parámetros a «{ret_val.func.id}».",
                            lazy_recommendation=f"Usa directamente «{ret_val.func.id}» o un alias directo («{node.name} = {ret_val.func.id}»).",
                        )
                    )

        self.generic_visit(node)


def scan_stdlib_reimplements(code: str) -> List[PonytailViolation]:
    """Peldaño 3: Detección de reinvención de utilidades que ya existen en la biblioteca estándar."""
    violations: List[PonytailViolation] = []

    # Reimplementación de lectura simple de archivos en lugar de Path.read_text
    read_text_pattern = re.compile(
        r"with\s+open\(([^,]+),\s*['\"]r['\"]\)\s+as\s+\w+:\s*\n\s*\w+\s*=\s*\w+\.read\(\)",
        re.MULTILINE,
    )
    for m in read_text_pattern.finditer(code):
        violations.append(
            PonytailViolation(
                rung=3,
                name="Reinvención de pathlib.Path.read_text",
                severity="LOW",
                location="Bloque with open(...) as f: f.read()",
                description="Se utiliza un bloque de contexto multilínea manual para leer un archivo de texto plano completo.",
                lazy_recommendation="Usa «Path(filepath).read_text(encoding='utf-8')» de la biblioteca estándar.",
            )
        )

    # Reimplementación de diccionario de frecuencias en lugar de collections.Counter
    counter_pattern = re.compile(
        r"for\s+\w+\s+in\s+\w+:\s*\n\s*if\s+\w+\s+not\s+in\s+(\w+):\s*\n\s*\1\[\w+\]\s*=\s*0\s*\n\s*\1\[\w+\]\s*\+=\s*1",
        re.MULTILINE,
    )
    for m in counter_pattern.finditer(code):
        violations.append(
            PonytailViolation(
                rung=3,
                name="Reinvención de collections.Counter",
                severity="LOW",
                location="Bucle de conteo manual en diccionario",
                description="Bucle manual de 4 líneas para calcular frecuencias de elementos.",
                lazy_recommendation="Usa «collections.Counter(elementos)» de la biblioteca estándar.",
            )
        )

    # Reimplementación de aplanado de listas en lugar de itertools.chain
    flatten_pattern = re.compile(
        r"(\w+)\s*=\s*\[\]\s*\n\s*for\s+\w+\s+in\s+\w+:\s*\n\s*for\s+\w+\s+in\s+\w+:\s*\n\s*\1\.append\(",
        re.MULTILINE,
    )
    for m in flatten_pattern.finditer(code):
        violations.append(
            PonytailViolation(
                rung=3,
                name="Reinvención de itertools.chain",
                severity="LOW",
                location="Bucles anidados para aplanar listas",
                description="Doble bucle for imperativo para concatenar sublistas.",
                lazy_recommendation="Usa «list(itertools.chain.from_iterable(listas))» o una comprensión simple.",
            )
        )

    return violations


def scan_native_platform_violations(code: str) -> List[PonytailViolation]:
    """Peldaño 4: Detección de llamadas a comandos shell cuando la plataforma o python lo hace nativo."""
    violations: List[PonytailViolation] = []

    # Subprocess para cat, grep, rm, mkdir
    shell_commands = [
        ("rm ", "os.remove() o shutil.rmtree()"),
        ("cat ", "Path.read_text()"),
        ("mkdir ", "Path.mkdir(parents=True, exist_ok=True)"),
        ("cp ", "shutil.copy()"),
    ]
    for cmd, repl in shell_commands:
        if f'"{cmd}' in code or f"'{cmd}" in code or f'["{cmd.strip()}"' in code:
            violations.append(
                PonytailViolation(
                    rung=4,
                    name=f"Invocación Externa Innecesaria ({cmd.strip()})",
                    severity="MEDIUM",
                    location=f"Comando de shell: {cmd.strip()}",
                    description=f"Se invoca el binario externo del sistema operativo «{cmd.strip()}» mediante subproceso.",
                    lazy_recommendation=f"Usa la alternativa nativa de Python: {repl}.",
                )
            )

    return violations


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula la distancia de Levenshtein entre dos cadenas en memoria O(min(m, n))."""
    if s1 == s2:
        return 0
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if not s2:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def detect_lexical_confusion(code_content: str) -> List[str]:
    """Identifica variables con nombres engañosamente similares en el código (inspirado en RapidFuzz)."""
    warnings: List[str] = []
    names = set()

    try:
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if len(node.id) >= 4 and not node.id.startswith("__"):
                    names.add(node.id)
            elif isinstance(node, ast.arg):
                if len(node.arg) >= 4 and not node.arg.startswith("__"):
                    names.add(node.arg)
    except SyntaxError:
        tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b", code_content)
        names = set(tokens)

    name_list = sorted(list(names))
    seen_pairs = set()

    for i in range(len(name_list)):
        for j in range(i + 1, len(name_list)):
            n1, n2 = name_list[i], name_list[j]
            # Si uno es prefijo del otro o tienen distancia <= 2
            dist = levenshtein_distance(n1.lower(), n2.lower())
            if 0 < dist <= 2 and abs(len(n1) - len(n2)) <= 2:
                pair_key = tuple(sorted([n1, n2]))
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    warnings.append(
                        f"Riesgo de confusión cognitiva a las 3:00 AM: «{n1}» vs. «{n2}» (distancia {dist}). "
                        "Nombres fonética o visualmente similares pueden inducir intercambio involuntario de variables."
                    )
            if len(warnings) >= 5:
                break
        if len(warnings) >= 5:
            break

    return warnings


def calculate_visual_clutter(code_content: str) -> float:
    """Calcula el índice de saturación y ruido visual del código (0 % a 100 %)."""
    lines = code_content.splitlines()
    if not lines:
        return 0.0

    decorative_comment_lines = 0
    deep_indent_lines = 0
    long_lines = 0

    for line in lines:
        stripped = line.strip()
        # Comentarios decorativos repetitivos (ej. # --------------)
        if stripped.startswith("#") and any(seq in stripped for seq in ("---", "===", "***", "###")):
            decorative_comment_lines += 1
        # Líneas con sangría profunda (≥ 16 espacios o 4 tabulaciones)
        indent_spaces = len(line) - len(line.lstrip(" "))
        if indent_spaces >= 16:
            deep_indent_lines += 1
        # Líneas sobreextendidas (> 100 caracteres)
        if len(line) > 100:
            long_lines += 1

    total = len(lines)
    clutter_ratio = (
        (decorative_comment_lines * 1.5 + deep_indent_lines * 2.0 + long_lines * 0.8) / total
    ) * 100.0

    return round(min(100.0, clutter_ratio), 1)


def audit_ponytail(code_content: str, max_acceptable_bloat: float = 25.0) -> PonytailAuditReport:
    """Ejecuta la auditoría integral de Ponytail sobre el código fuente aplicando la Escalera de la Pereza."""
    lines = code_content.splitlines()
    total_lines = len(lines)

    violations: List[PonytailViolation] = []

    # 1. Auditoría de AST si es Python
    try:
        tree = ast.parse(code_content)
        visitor = PonytailVisitor(lines)
        visitor.visit(tree)
        violations.extend(visitor.violations)

        # Regla de los Tres Golpes (Three Strikes Rule)
        abstract_classes = set()
        concrete_impls: Dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_abstract = any(
                    getattr(base, "id", "") in ("ABC", "AbstractServer") for base in node.bases
                )
                if is_abstract:
                    abstract_classes.add(node.name)
                for base in node.bases:
                    base_id = getattr(base, "id", "")
                    if base_id:
                        concrete_impls[base_id] = concrete_impls.get(base_id, 0) + 1

        for abc_name in abstract_classes:
            impl_count = concrete_impls.get(abc_name, 0)
            if impl_count < 3:
                violations.append(
                    PonytailViolation(
                        rung=1,
                        name="Violación de la Regla de los Tres Golpes (Three Strikes Rule)",
                        severity="MEDIUM",
                        location=f"class {abc_name}",
                        description=(
                            f"Se definió la abstracción prematura «{abc_name}» con solo {impl_count} implementación(es) concreta(s). "
                            "No abstraigas hasta que lo hayas escrito tres veces. La duplicación temprana es más económica que la abstracción equivocada."
                        ),
                        lazy_recommendation="Poda la clase abstracta y utiliza una función o clase directa hasta tener al menos 3 casos reales.",
                    )
                )

    except SyntaxError as err:
        logger.debug("El contenido no se pudo parsear como AST de Python: %s", err)

    # 2. Peldaño 3: Stdlib reimplementation
    violations.extend(scan_stdlib_reimplements(code_content))

    # 3. Peldaño 4: Native platform
    violations.extend(scan_native_platform_violations(code_content))

    # Conteo por peldaño
    ladder_summary: Dict[str, int] = {}
    for v in violations:
        key = f"Peldaño {v.rung}: {v.name}"
        ladder_summary[key] = ladder_summary.get(key, 0) + 1

    # Cálculo del Bloat Score y líneas reducibles
    weight_map = {"CRITICAL": 25.0, "HIGH": 15.0, "MEDIUM": 8.0, "LOW": 3.0}
    raw_score = sum(weight_map.get(v.severity, 5.0) for v in violations)

    # Normalización del score entre 0 y 100
    bloat_score = min(100.0, raw_score)

    lines_reducible = sum(4 if v.severity in ("HIGH", "CRITICAL") else 2 for v in violations)
    lines_reducible = min(total_lines, lines_reducible)

    is_acceptable = bloat_score <= max_acceptable_bloat

    return PonytailAuditReport(
        bloat_score=round(bloat_score, 1),
        lines_analyzed=total_lines,
        estimated_lines_reducible=lines_reducible,
        violations=violations,
        ladder_summary=ladder_summary,
        is_acceptable=is_acceptable,
    )
