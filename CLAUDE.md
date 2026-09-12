# Directrices de Claude Code para el Repositorio Six Hats

Este proyecto implementa la metodología de los **Seis Sombreros para Pensar** (*Six Thinking Hats*) de Edward de Bono aplicada a la ingeniería de software, arquitectura de sistemas y revisión de código forense.

Como asistente que opera a través de **Claude Code**, debes integrar metódicamente esta disciplina analítica en cada interacción, diagnóstico y propuesta de cambio.

---

## Servidor MCP y Herramientas Disponibles

El servidor MCP `six-hats` está configurado y accesible. Si ejecutas en un entorno nuevo, puedes añadirlo con:
```bash
claude mcp add six-hats uvx six-hats mcp
```

### Catálogo de Herramientas MCP
1. `six_hats_review(code_diff: str, task_context: str = "", is_diff: bool = false)`:
   - Ejecuta la deliberación paralela de los 6 sombreros.
   - Provee telemetría AST, complejidad ciclomática de McCabe, complejidad cognitiva de SonarSource, índice de mantenibilidad, análisis adversarial de seguridad (CWE/OWASP), cálculo de entropía de Shannon, trampas de rendimiento $O(n^2)$, filtro anti-sobreingeniería Ponytail y parche unificado de mitigación.
2. `six_hats_debate(architecture_proposal: str)`:
   - Confronta dialécticamente una propuesta entre el Sombrero Negro (Riesgos/Costos ocultos) y el Sombrero Verde (Innovación/Disrupción), con síntesis del Sombrero Azul.
3. `six_hats_quick_check(code_diff: str)`:
   - Chequeo rápido de la tríada crítica: Hechos (Blanco), Riesgos (Negro) y Valor (Amarillo).
4. `six_hats_ponytail_audit(code: str, threshold: float = 25.0)`:
   - Auditoría estricta contra la Escalera de la Pereza de Ponytail para extirpar sobreingeniería, capas especulativas y clases innecesarias.

---

## Protocolo de Razonamiento de los Seis Sombreros

Cuando analices código, resuelvas incidencias o propongas diseños arquitectónicos, estructura tu respuesta respetando las perspectivas:

- ⚪ **[Sombrero Blanco] (Hechos y Telemetría):** Apóyate en datos empíricos, métricas estáticas, complejidad ciclomática y cobertura real. Prohibido especular sin evidencia.
- 🟢 **[Sombrero Verde] (Innovación Lateral):** Genera alternativas disruptivas (estructuras zero-copy, paradigmas funcionales inmutables o arquitecturas reactivas desacopladas). Explica siempre el *trade-off* de cada alternativa.
- ⚫ **[Sombrero Negro] (Juicio Crítico y Seguridad):** Identifica puntos únicos de fallo, condiciones de carrera, vectores de inyección y riesgos operacionales con severidad (CRITICAL, HIGH, MEDIUM, LOW).
- 🟡 **[Sombrero Amarillo] (Valor y Eficiencia):** Modela los beneficios tangibles, reducciones de latencia, optimizaciones de throughput y viabilidad operativa.
- 🔴 **[Sombrero Rojo] (DX y Ergonomía Ponytail):** Evalúa la legibilidad del código a las 3:00 AM, la carga cognitiva y aplica el principio de la Escalera de la Pereza para podar abstracciones innecesarias.
- 🔵 **[Sombrero Azul] (Orquestación y Síntesis):** Emite el veredicto ejecutivo final, mitiga los riesgos críticos y genera parches limpios y aplicables.

---

## Estándares Lingüísticos y Ortotipográficos (RAE / Chile)

1. **Jerarquía de comillas:** Usa comillas angulares (`« »`) como comillas primarias; comillas inglesas (`" "`) solo dentro de citas; comillas simples (`' '`) en tercer nivel.
2. **Puntuación exterior:** Los signos de puntuación van siempre fuera de las comillas de cierre: `«ejemplo», «ejemplo».`
3. **Signos dobles obligatorios:** Abre siempre con `¿` e `¡` y cierra con `?` y `!`. Jamás agregues punto tras `?` o `!`.
4. **Raya de inciso (`—`):** Pegada a la palabra inicial y final del inciso (`palabra —inciso— palabra`).
5. **Cifras y porcentajes:** Espacio obligatorio antes del símbolo `%` (`100 %`, `25 %`). Usa coma decimal para cifras en español (`0,45`).
6. **Titulares:** Los encabezados y títulos no llevan punto final.

---

## Comandos Frecuentes de Desarrollo

- **Ejecutar pruebas unitarias:**
  ```bash
  .venv/bin/pytest tests/ -v
  ```
- **Auditoría de sobreingeniería con CLI:**
  ```bash
  .venv/bin/six-hats ponytail <archivo> --threshold 25.0
  ```
- **Revisión completa con reporte SARIF:**
  ```bash
  .venv/bin/six-hats review <archivo> --sarif reporte.sarif
  ```
- **Exportar esquemas para agentes:**
  ```bash
  .venv/bin/six-hats export-tools --format [openai|hermes|claude|mcp]
  ```
