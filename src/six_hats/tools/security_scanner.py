"""Escáner forense de seguridad y análisis adversarial para el Sombrero Negro.

Inspirado en los motores Semgrep, Bandit y Gitleaks para detectar vulnerabilidades OWASP,
CWEs, fallos de inyección, deserialización insegura y exposición de secretos.
"""

import ast
import re
import logging
from typing import List
from six_hats.core.models import BlackHatFinding

logger = logging.getLogger("six_hats.security_scanner")


SECRET_PATTERNS = [
    (
        "AWS Access Key ID",
        re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        "CWE-798: Uso de Credenciales Codificadas en Duro",
    ),
    (
        "JSON Web Token (JWT)",
        re.compile(r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"),
        "CWE-798: Token de Autenticación Expuesto",
    ),
    (
        "Clave Privada RSA / SSH",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
        "CWE-312: Almacenamiento de Secretos en Texto Claro",
    ),
    (
        "API Key Genérica",
        re.compile(r"""(?i)(?:api_key|apikey|secret_key|auth_token)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]"""),
        "CWE-798: Secreto Estático en Código",
    ),
]


class SecurityAstVisitor(ast.NodeVisitor):
    """Inspección sintáctica de AST para patrones de Bandit y Semgrep."""

    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.findings: List[BlackHatFinding] = []

    def visit_Call(self, node: ast.Call):
        # 1. Detección de eval() y exec()
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.findings.append(
                    BlackHatFinding(
                        severity="CRITICAL",
                        risk_type="Inyección de Código Arbitrario (CWE-94 / CWE-95)",
                        location=f"Línea {node.lineno}: {node.func.id}(...)",
                        description=f"Invocación directa de «{node.func.id}()». Permite la ejecución de instrucciones arbitrarias por inyección de cadenas.",
                        cwe_owasp_id="CWE-94",
                        remediation="Evitar ejecución dinámica; utilizar serialización estructurada o intérpretes de expresiones restringidos.",
                    )
                )

        # 2. Detección de shell=True en subprocess
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("Popen", "run", "call", "check_call", "check_output"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append(
                        BlackHatFinding(
                            severity="CRITICAL",
                            risk_type="Inyección de Comandos Shell (CWE-78 / Bandit B602)",
                            location=f"Línea {node.lineno}: subprocess.{node.func.attr}(..., shell=True)",
                            description="La bandera shell=True ejecuta comandos a través de la shell del sistema, exponiendo el proceso a inyección de comandos.",
                            cwe_owasp_id="CWE-78",
                            remediation="Pasar argumentos como lista y eliminar shell=True.",
                        )
                    )

        # 3. Deserialización insegura con pickle o yaml
        if isinstance(node.func, ast.Attribute):
            # pickle.loads / pickle.load
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle" and node.func.attr in ("load", "loads"):
                self.findings.append(
                    BlackHatFinding(
                        severity="CRITICAL",
                        risk_type="Deserialización Insegura de Objetos (CWE-502 / Bandit B301)",
                        location=f"Línea {node.lineno}: pickle.{node.func.attr}(...)",
                        description="Deserializar streams no confiables mediante pickle permite la ejecución arbitraria de código durante el unpickling.",
                        cwe_owasp_id="CWE-502",
                        remediation="Utilizar formatos declarativos seguros como JSON, Protocol Buffers o MessagePack.",
                    )
                )
            # yaml.load sin Loader seguro
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ("yaml", "pyyaml") and node.func.attr == "load":
                has_safe_loader = any(
                    kw.arg == "Loader" and getattr(kw.value, "id", "") in ("SafeLoader", "CSafeLoader")
                    for kw in node.keywords
                )
                if not has_safe_loader:
                    self.findings.append(
                        BlackHatFinding(
                            severity="HIGH",
                            risk_type="Deserialización Insegura en YAML (CWE-502 / Bandit B506)",
                            location=f"Línea {node.lineno}: yaml.load(...)",
                            description="Uso de yaml.load sin SafeLoader. Utilice yaml.safe_load() para prevenir instanciación arbitraria de objetos.",
                            cwe_owasp_id="CWE-502",
                            remediation="Usar yaml.safe_load(stream).",
                        )
                    )

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # 4. Supresión silenciosa de errores: except: pass o except Exception: pass
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            type_name = "genérica" if node.type is None else getattr(node.type, "id", "desconocida")
            self.findings.append(
                BlackHatFinding(
                    severity="HIGH",
                    risk_type="Supresión Silenciosa de Excepciones (CWE-391)",
                    location=f"Línea {node.lineno}: except {type_name}: pass",
                    description="El bloque try-except oculta fallos de sistema sin registrarlos ni relanzarlos, enmascarando corrupción de estado.",
                    cwe_owasp_id="CWE-391",
                    remediation="Registrar la excepción con logging.exception() o relanzarla.",
                )
            )

        self.generic_visit(node)


import math
from collections import Counter


def calculate_shannon_entropy(data: str) -> float:
    """Calcula la entropía de Shannon en bits/carácter (inspirado en TruffleHog)."""
    if not data or len(data) < 2:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def generate_property_invariants(code_content: str) -> List[str]:
    """Genera casos límite e invariantes de prueba por propiedades basados en Hypothesis."""
    invariants: List[str] = []
    lower_code = code_content.lower()

    if any(k in lower_code for k in ("str", "text", "path", "url", "query", "payload")):
        invariants.append(
            "Fuzzing de Cadenas (Hypothesis): Probar cadena vacía (''), caracteres nulos ('\\x00'), "
            "espacios en blanco, secuencias Unicode multilingües (RTL) y longitud extrema (10 MB)."
        )

    if any(k in lower_code for k in ("int", "float", "count", "size", "limit", "offset", "timeout", "port")):
        invariants.append(
            "Fuzzing Numérico (Hypothesis): Probar valores de frontera: 0, -1, sys.maxsize, enteros "
            "negativos de 64 bits, NaN y divisiones por cero."
        )

    if any(k in lower_code for k in ("list", "dict", "items", "records", "batch", "elements")):
        invariants.append(
            "Invariante de Colecciones: Garantizar que el comportamiento sea determinista con colección vacía [], "
            "con un solo elemento, con 100 000 elementos y ante referencias nulas (None)."
        )

    invariants.append(
        "Invariante de Idempotencia / Preservación: Verificar que la ejecución reiterada no corrompa el estado "
        "global y que ante fallos transitorios la función limpie sus recursos (conexiones/descriptores)."
    )

    return invariants


def scan_security_vulnerabilities(code_content: str) -> List[BlackHatFinding]:
    """Ejecuta un escaneo adversarial completo buscando vulnerabilidades y secretos expuestos."""
    findings: List[BlackHatFinding] = []
    lines = code_content.splitlines()

    # 1. Escaneo AST
    try:
        tree = ast.parse(code_content)
        visitor = SecurityAstVisitor(lines)
        visitor.visit(tree)
        findings.extend(visitor.findings)

        # 1.1 Detección de cadenas literales de alta entropía (TruffleHog)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value.strip()
                # Descartar URLs, expresiones regulares y cadenas con espacios
                is_regex = any(r in val for r in ("(?:", "(?P", "\\d", "\\w", "\\s", "(?i)", ".*", ".+", "[a-z", "[A-Z"))
                if len(val) >= 24 and not val.startswith("http") and " " not in val and not is_regex:
                    entropy = calculate_shannon_entropy(val)
                    if entropy >= 4.5:
                        findings.append(
                            BlackHatFinding(
                                severity="HIGH",
                                risk_type="Cadena de Alta Entropía / Secreto Criptográfico (CWE-798)",
                                location=f"Línea {getattr(node, 'lineno', '?')}: literal con entropía Shannon {round(entropy, 2)} bits",
                                description=(
                                    f"La cadena «{val[:8]}...» presenta una entropía excepcionalmente alta ({round(entropy, 2)}), "
                                    "típica de tokens de API, hashes o claves privadas no declaradas en variables de entorno."
                                ),
                                cwe_owasp_id="CWE-798",
                                remediation="Extraer el secreto a variables de entorno o gestor de credenciales (KMS / Vault).",
                            )
                        )
    except SyntaxError as err:
        logger.debug("Código no parseable como AST de Python: %s", err)

    # 2. Detección de Secretos y Tokens con patrones Gitleaks
    for line_idx, line in enumerate(lines, 1):
        if "re.compile" in line or "SECRET_PATTERNS" in line:
            continue
        for name, pattern, cwe in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(
                    BlackHatFinding(
                        severity="CRITICAL",
                        risk_type=f"Exposición de Credenciales: {name} ({cwe})",
                        location=f"Línea {line_idx}: {line.strip()[:40]}...",
                        description="Se detectó una credencial, clave privada o token criptográfico en texto plano dentro del código fuente.",
                    )
                )

    # 3. Path Traversal en operaciones de filesystem (CWE-22)
    traversal_pattern = re.compile(r"""(?:open|Path|read_text|write_text|os\.(?:path|listdir|walk|remove))\s*\([^)]*['"][^'"]*(\.\./|\.\.\\)""")
    if traversal_pattern.search(code_content):
        findings.append(
            BlackHatFinding(
                severity="MEDIUM",
                risk_type="Riesgo de Salto de Directorio / Path Traversal (CWE-22)",
                location="Uso de secuencia relativa «../» en operaciones de archivo",
                description="La manipulación de rutas con «../» sin validar con Path.resolve() o os.path.abspath puede exponer archivos sensibles del sistema operativo.",
            )
        )

    # 4. Invocaciones de red sin timeout explícito
    if any(req in code_content for req in ("requests.get", "requests.post", "httpx.get", "httpx.post", "urllib.request")):
        if "timeout=" not in code_content and "timeout " not in code_content:
            findings.append(
                BlackHatFinding(
                    severity="HIGH",
                    risk_type="Llamada de Red sin Timeout (CWE-400: Agotamiento de Recursos)",
                    location="Petición HTTP externa",
                    description="Las peticiones de red sin timeout explícito pueden colgar el hilo o worker indefinidamente ante degradaciones de red.",
                )
            )

    # Inyectar invariantes de propiedad generadas estilo Hypothesis en los hallazgos
    property_invariants = generate_property_invariants(code_content)
    for f in findings:
        f.property_invariants = property_invariants

    # Si no se detectaron fallos de severidad crítica/alta, agregar recomendación de defensa en profundidad
    if not findings:
        findings.append(
            BlackHatFinding(
                severity="LOW",
                risk_type="Principio de Mínimo Privilegio y Aislamiento",
                location="Configuración general",
                description="No se identificaron vulnerabilidades directas OWASP Top 10. Mantener validación defensiva en puntos de entrada.",
                property_invariants=property_invariants,
            )
        )

    return findings
