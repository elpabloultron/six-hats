import json
from mcp.server.mcpserver import MCPServer
from six_hats.core.orchestrator import SixHatsOrchestrator

app = MCPServer("six-hats")
orchestrator = SixHatsOrchestrator()


@app.tool()
async def six_hats_review(code_diff: str, task_context: str = "", is_diff: bool = False) -> str:
    """Ejecuta un análisis multifacético y exhaustivo de código usando los 6 sombreros de Edward de Bono en paralelo.

    Args:
        code_diff: Diff unificado o contenido completo del archivo a evaluar.
        task_context: Contexto de la tarea, requerimiento arquitectónico o problema a resolver.
        is_diff: Indica si el input es un diff unificado de git (true) o código completo (false).
    """
    result = await orchestrator.run_full_cycle(
        code_content=code_diff,
        is_diff=is_diff,
        task_context=task_context,
    )
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)


@app.tool()
async def six_hats_debate(architecture_proposal: str) -> str:
    """Lanza un debate adversarial entre Sombrero Negro (Riesgos/Vulnerabilidades) y Sombrero Verde (Innovación) moderado por Sombrero Azul.

    Args:
        architecture_proposal: Propuesta arquitectónica o técnica a desafiar y evaluar.
    """
    result = await orchestrator.run_debate(architecture_proposal=architecture_proposal)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool()
async def six_hats_quick_check(code_diff: str) -> str:
    """Evaluación rápida focalizada en la tríada crítica: Blanco (Hechos/AST), Negro (Riesgos) y Amarillo (Valor).

    Args:
        code_diff: Código o diff sobre el cual extraer hechos y contrastar pros y contras.
    """
    result = await orchestrator.run_critics(code_content=code_diff)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool()
async def six_hats_ponytail_audit(code: str, threshold: float = 25.0) -> str:
    """Ejecuta una auditoría estricta contra la Escalera de la Pereza de Ponytail para detectar sobreingeniería y código superfluo.

    Args:
        code: Contenido del archivo o fragmento de código a auditar.
        threshold: Umbral máximo admisible de sobreingeniería (por defecto 25.0 %).
    """
    result = await orchestrator.run_ponytail_audit(code_content=code, max_acceptable_bloat=threshold)
    return json.dumps(result, indent=2, ensure_ascii=False)


# ============================================================================
# Prompts MCP Nativos (Estándar Oficial Model Context Protocol)
# Permiten a la IA anfitriona (Antigravity, Claude, Cursor, Ollama) asumir
# los roles metodológicos sin requerir APIs de LLM externas en el servidor.
# ============================================================================


@app.prompt(
    name="six_hats_deliberation",
    title="Deliberación Completa Seis Sombreros",
    description="Protocolo maestro de deliberación secuencial y paralela con los Seis Sombreros para la IA anfitriona.",
)
def six_hats_deliberation(task_context: str, code_content: str = "") -> str:
    """Instrucciones maestras para que la IA anfitriona ejecute el ciclo completo de los Seis Sombreros."""
    prompt = (
        "Adopta el protocolo metodológico de los Seis Sombreros para Pensar (Edward de Bono) "
        f"para abordar la siguiente tarea o problema:\n\n"
        f"CONTEXTO DE LA TAREA:\n{task_context}\n\n"
    )
    if code_content:
        prompt += f"CÓDIGO FUENTE O PROPUESTA A EVALUAR:\n```\n{code_content}\n```\n\n"

    prompt += (
        "INSTRUCCIONES DE DELIBERACIÓN PARA LA IA ANFITRIONA:\n"
        "1. [⚪ Sombrero Blanco]: Consulta hechos puros o utiliza la herramienta `six_hats_review` para extraer la "
        "telemetría exacta de AST, complejidad ciclomática de McCabe y cognitiva de SonarSource.\n"
        "2. [🟢 Sombrero Verde]: Plantea al menos 3 alternativas arquitectónicas radicalmente divergentes (inversión de "
        "supuestos, zero-copy, funcional inmutable o desacoplamiento reactivo).\n"
        "3. [⚫ Sombrero Negro]: Ejecuta una auditoría adversarial implacable. Busca puntos únicos de fallo, "
        "condiciones de carrera, inyecciones, fugas de recursos y clasifica por severidad (CRITICAL, HIGH, MEDIUM, LOW).\n"
        "4. [🟡 Sombrero Amarillo]: Modela el valor tangible, ganancias de rendimiento (throughput, latencia) y "
        "mantenibilidad a largo plazo de las alternativas viables.\n"
        "5. [🔴 Sombrero Rojo]: Evalúa la experiencia de desarrollo (DX), la legibilidad a las 3:00 AM y aplica la "
        "Escalera de la Pereza de Ponytail para vetar cualquier sobreingeniería innecesaria.\n"
        "6. [🔵 Sombrero Azul]: Sintetiza el dictamen final, mitiga obligatoriamente los riesgos críticos y genera "
        "la solución definitiva en formato de parche unificado (unified diff)."
    )
    return prompt


@app.prompt(
    name="hat_green_creative",
    title="Sombrero Verde: Pensamiento Lateral",
    description="Protocolo para que la IA anfitriona genere alternativas arquitectónicas disruptivas e innovadoras.",
)
def hat_green_creative(task_context: str, code_content: str = "") -> str:
    """Prompt especializado para la ideación del Sombrero Verde."""
    prompt = (
        "ACTÚA COMO EL SOMBRERO VERDE (Creatividad y Pensamiento Lateral de Edward de Bono).\n"
        "Tu objetivo es romper bloqueos cognitivos y concebir soluciones técnicas no convencionales.\n\n"
        f"CONTEXTO O DESAFÍO:\n{task_context}\n\n"
    )
    if code_content:
        prompt += f"CÓDIGO BASE:\n```\n{code_content}\n```\n\n"

    prompt += (
        "REGLAS OBLIGATORIAS:\n"
        "1. Queda estrictamente prohibido conformarse con la solución obvia o convencional.\n"
        "2. Diseña al menos 3 alternativas de arquitectura profundamente divergentes:\n"
        "   - Alternativa A: Paradigma Funcional Inmutable con manejo explícito de errores (Result monádico).\n"
        "   - Alternativa B: Arquitectura Reactiva / Event-Driven con colas o streaming desacoplado.\n"
        "   - Alternativa C: Estructuras Zero-Copy con buffers continuos de alto rendimiento.\n"
        "3. Para cada propuesta, explicita su compromiso o costo central (*trade-off*)."
    )
    return prompt


@app.prompt(
    name="hat_black_adversarial",
    title="Sombrero Negro: Auditoría Adversarial",
    description="Protocolo para que la IA anfitriona realice una auditoría destructiva, análisis de riesgos y caos.",
)
def hat_black_adversarial(code_content: str, task_context: str = "") -> str:
    """Prompt especializado para el juicio crítico del Sombrero Negro."""
    prompt = (
        "ACTÚA COMO EL SOMBRERO NEGRO (Juicio Crítico, Auditoría Adversarial y Cautela Forense).\n"
        "Tu misión es encontrar todas las formas en que este sistema puede fallar, romperse o ser vulnerado.\n\n"
    )
    if task_context:
        prompt += f"CONTEXTO DEL SISTEMA:\n{task_context}\n\n"
    prompt += (
        f"CÓDIGO A AUDITAR:\n```\n{code_content}\n```\n\n"
        "REGLAS DE EVALUACIÓN:\n"
        "1. Asume hostilidad en los datos de entrada y fallos en la infraestructura (red, memoria, disco).\n"
        "2. Identifica puntos únicos de fallo (SPOF), cuellos de botella, condiciones de carrera y vulnerabilidades "
        "CWE/OWASP (inyección, deserialización, secretos expuestos, omisión de excepciones).\n"
        "3. Clasifica cada riesgo con su nivel de gravedad: CRITICAL, HIGH, MEDIUM o LOW, indicando ubicación y remediación."
    )
    return prompt


@app.prompt(
    name="hat_blue_synthesis",
    title="Sombrero Azul: Mediación y Dictamen Final",
    description="Protocolo para que la IA anfitriona ejerza el control metacognitivo, aplique el veto Ponytail y sintetice el parche unificado.",
)
def hat_blue_synthesis(task_context: str, forensic_data: str = "", code_content: str = "") -> str:
    """Prompt especializado para la orquestación y cierre del Sombrero Azul."""
    prompt = (
        "ACTÚA COMO EL SOMBRERO AZUL (Líder Orquestador, Mediador Dialéctico y Síntesis Final).\n"
        "Tu objetivo es coordinar los resultados de los sombreros previos, balancear compromisos y generar la solución final.\n\n"
        f"CONTEXTO DE LA DELIBERACIÓN:\n{task_context}\n\n"
    )
    if forensic_data:
        prompt += f"DATOS FORENSES Y DICTÁMENES PREVIOS:\n{forensic_data}\n\n"
    if code_content:
        prompt += f"CÓDIGO ORIGINAL:\n```\n{code_content}\n```\n\n"

    prompt += (
        "DIRECTRICES DE RESOLUCIÓN:\n"
        "1. Mitiga con carácter obligatorio todos los riesgos identificados como CRITICAL y HIGH por el Sombrero Negro.\n"
        "2. Aplica el Veto de Simplicidad de Ponytail: si la propuesta añade sobreingeniería innecesaria, poda las "
        "capas superfluas respetando el principio YAGNI.\n"
        "3. Emite un dictamen ejecutivo estructurado: Veredicto (APPROVE / REQUIRE_CHANGES), Arquitectura seleccionada, "
        "mitigaciones incorporadas y el parche unificado final en formato unified diff listo para aplicar con `git apply`."
    )
    return prompt


@app.prompt(
    name="six_hats_debate",
    title="Debate Dialéctico Negro vs. Verde",
    description="Protocolo para confrontación estructurada entre Sombrero Negro (Cautela) y Sombrero Verde (Innovación).",
)
def six_hats_debate_prompt(architecture_proposal: str) -> str:
    """Prompt para conducir un debate adversarial sobre una propuesta técnica."""
    return (
        "CONDUCE UN DEBATE DIALÉCTICO METODOLÓGICO: SOMBRERO NEGRO VS. SOMBRERO VERDE\n\n"
        f"PROPUESTA ARQUITECTÓNICA A DEBATIR:\n{architecture_proposal}\n\n"
        "ESTRUCTURA DEL DEBATE:\n"
        "1. Tesis (🟢 Sombrero Verde): Expón la visión más ambiciosa de la propuesta, sus fortalezas disruptivas "
        "y los paradigmas modernos que aprovecha.\n"
        "2. Antítesis (⚫ Sombrero Negro): Ataca implacablemente la propuesta identificando costos ocultos, "
        "puntos únicos de fallo, complejidad operativa, curvas de aprendizaje y escenarios de colapso.\n"
        "3. Réplica Creativa (🟢 Sombrero Verde): Propón adaptaciones que neutralicen las objeciones del Sombrero Negro "
        "sin perder la esencia innovadora.\n"
        "4. Síntesis y Veredicto (🔵 Sombrero Azul): Dictamina la viabilidad final, balancea los riesgos reales contra "
        "el valor obtenido y define las condiciones obligatorias para avanzar."
    )


def main():
    """Punto de entrada para el servidor MCP en modo STDIO."""
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
