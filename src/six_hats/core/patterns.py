"""Catálogo formal de patrones de diseño arquitectónico para el Sombrero Verde.

Inspirado en faif/python-patterns y dry-python/returns para idear alternativas
radicalmente divergentes y no convencionales.
"""

from typing import List
from six_hats.core.models import GreenHatProposal


ARCHITECTURAL_CATALOG = [
    GreenHatProposal(
        name="Pipeline Funcional Inmutable con Contenedores Result",
        paradigm="Funcional / Tipado Estricto (inspirado en dry-python/returns)",
        description=(
            "Transformar el código imperativo en una composición monádica pura basada en tipos Result[Success, Failure]. "
            "Elimina las mutaciones de estado intermedias y el lanzamiento indiscriminado de excepciones no controladas."
        ),
        tradeoff="Curva de aprendizaje moderada para desarrolladores acostumbrados al flujo imperativo con try/except.",
    ),
    GreenHatProposal(
        name="Patrón Reactor Asíncrono con Canales CSP",
        paradigm="Concurrencia Reactiva / Colas de Mensajes (Event-Driven)",
        description=(
            "Desacoplar la ingesta y el procesamiento mediante colas en memoria (asyncio.Queue) y un conjunto de trabajadores "
            "independientes. Previene el bloqueo del hilo principal y absorbe picos de tráfico con contrapresión (backpressure)."
        ),
        tradeoff="Introduce eventual consistency y mayor dificultad en el rastreo de trazas de ejecución en logs secuenciales.",
    ),
    GreenHatProposal(
        name="Estructuras Zero-Copy y Buffers Continuos",
        paradigm="Rendimiento Crítico / Vistas de Memoria (Zero-Alloc)",
        description=(
            "Operar directamente sobre porciones de memoria compartida preasignada (memoryview, bytearray, arrays contiguos) "
            "y generadores perezosos. Evita la instanciación de objetos efímeros en el recolector de basura (GC)."
        ),
        tradeoff="Restringido a tipos de datos planos o binarios y exige una gestión rigurosa del ciclo de vida del buffer.",
    ),
    GreenHatProposal(
        name="Arquitectura Limpia con Puertos y Adaptadores",
        paradigm="Hexagonal / Inversión de Dependencias (DIP)",
        description=(
            "Separar las entidades y casos de uso del dominio de cualquier biblioteca externa o base de datos mediante interfaces "
            "(typing.Protocol). Permite intercambiar dependencias de infraestructura y mockear con cero fricción en tests."
        ),
        tradeoff="Incrementa la cantidad de archivos y capas iniciales; debe vigilarse contra la sobreingeniería (Ponytail).",
    ),
    GreenHatProposal(
        name="Tipado Estructural Puro con typing.Protocol (PEP 544)",
        paradigm="Duck-Typing Estático / Desacoplamiento Formal",
        description=(
            "Sustituir jerarquías de herencia rígidas por protocolos estructurales (typing.Protocol). "
            "Cualquier componente que satisfaga la signatura de métodos es intercambiable sin subclase forzada ni acoplamiento."
        ),
        tradeoff="Requiere linters y verificadores de tipo modernos (mypy/pyright) para validación estricta en compilación.",
    ),
    GreenHatProposal(
        name="Orquestación Resiliente con Actividades Idempotentes",
        paradigm="Tolerancia a Fallos / Sagas (inspirado en Temporal)",
        description=(
            "Descomponer operaciones críticas en pasos idempotentes con claves de desduplicación y reintentos con retroceso "
            "exponencial (exponential backoff) con jitter. Garantiza consistencia transaccional ante caídas de red o disco."
        ),
        tradeoff="Exige almacenamiento persistente para tokens de idempotencia o estado intermedio.",
    ),
]


def get_divergent_proposals(task_context: str = "", code_complexity: int = 1) -> List[GreenHatProposal]:
    """Selecciona y adapta al menos 3 propuestas arquitectónicas divergentes del catálogo."""
    selected = ARCHITECTURAL_CATALOG[:3]

    if "rendimiento" in task_context.lower() or "latencia" in task_context.lower() or code_complexity > 12:
        # Priorizar zero-alloc y reactor
        selected = [ARCHITECTURAL_CATALOG[2], ARCHITECTURAL_CATALOG[1], ARCHITECTURAL_CATALOG[0]]
    elif "seguridad" in task_context.lower() or "resiliencia" in task_context.lower():
        selected = [ARCHITECTURAL_CATALOG[0], ARCHITECTURAL_CATALOG[4], ARCHITECTURAL_CATALOG[1]]

    return selected


def generate_remediation_proposals(
    critical_findings: List[str], bloat_veto: bool = False
) -> List[GreenHatProposal]:
    """Genera propuestas creativas correctivas para el bucle de feedback del Sombrero Azul (LangGraph-style)."""
    proposals: List[GreenHatProposal] = []

    if bloat_veto:
        proposals.append(
            GreenHatProposal(
                name="Poda Radical Ponytail (Simplificación Funcional en Línea)",
                paradigm="Minimalismo YAGNI / Escalera de la Pereza",
                description=(
                    "Eliminar clases intermedias de un solo método y envoltorios especulativos. Reemplazar toda la sobreingeniería "
                    "por funciones puras de nivel superior y comprensiones de lista idiomáticas de la biblioteca estándar."
                ),
                tradeoff="El código pierde jerarquías ceremoniales pero gana velocidad de lectura instantánea a las 3:00 AM.",
            )
        )

    for finding in critical_findings:
        if "Inyección" in finding or "CWE-94" in finding or "CWE-78" in finding:
            proposals.append(
                GreenHatProposal(
                    name="Aislamiento Seguro mediante Intérprete AST Validador",
                    paradigm="Ejecución Segura / Sandboxing Declarativo",
                    description=(
                        "Sustituir invocaciones eval()/exec() o subprocess(shell=True) por un evaluador de AST en modo seguro "
                        "o mapeo de comandos en lista estricta con shlex.split(), sanitizando argumentos de forma estricta."
                    ),
                    tradeoff="Restringe la flexibilidad de sintaxis dinámica arbitraria en favor de seguridad inviolable.",
                )
            )
        elif "Secreto" in finding or "CWE-798" in finding:
            proposals.append(
                GreenHatProposal(
                    name="Inyección de Secretos por Variables de Entorno con Fallback Seguro",
                    paradigm="Twelve-Factor App / Seguridad Externa",
                    description=(
                        "Externalizar credenciales codificadas en duro mediante os.environ con verificación obligatoria "
                        "al arranque (falla rápido si falta la variable), integrando soporte para Vault o AWS Secrets Manager."
                    ),
                    tradeoff="Requiere configuración de entorno o archivos .env en desarrollo local.",
                )
            )

    if not proposals:
        proposals = ARCHITECTURAL_CATALOG[:3]

    # Asegurar al menos 3 propuestas
    while len(proposals) < 3:
        for p in ARCHITECTURAL_CATALOG:
            if p.name not in [x.name for x in proposals]:
                proposals.append(p)
                if len(proposals) >= 3:
                    break

    return proposals[:3]
