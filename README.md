# six-hats: Motor Multi-Agente de Razonamiento Paralelo y Servidor MCP

Motor multi-agente de deliberación y razonamiento paralelo basado en la metodología de los **Seis Sombreros para Pensar** (*Six Thinking Hats*) de Edward de Bono, diseñado para revisión de código, diseño arquitectónico, auditoría adversarial y depuración en Antigravity IDE y terminales CLI.

---

## 1. Fundamentos metodológicos y arquitectura Agent-Native

La técnica de los Seis Sombreros descompone el razonamiento técnico en modos cognitivos independientes y especializados para eliminar sesgos, evitar bloqueos y prevenir la interferencia de ego en la toma de decisiones:

* **⚪ Sombrero Blanco:** Hechos puros, extracción de AST políglota con Tree-sitter, complejidad ciclomática de McCabe, complejidad cognitiva (SonarSource), análisis de *Git Churn* / *Hotspots* (`pydriller`) y cobertura de pruebas.
* **🟢 Sombrero Verde:** Creatividad, pensamiento lateral, alternativas paradigmáticas divergentes (Zero-Copy, reactivo, funcional monádico ROP con `Result` y tipado estructural PEP 544 `Protocol`) y propuestas de remediación para bucles de feedback.
* **⚫ Sombrero Negro:** Juicio crítico, auditoría adversarial de vulnerabilidades (CWE/OWASP), detección de secretos por **Entropía de Shannon** (`trufflehog`) y generación de **Invariantes de Prueba por Propiedades** (`hypothesis` fuzzing).
* **🟡 Sombrero Amarillo:** Optimismo lógico, cálculo de valor, aceleración de throughput (20 % a 40 %) y **detección estática de trampas asintóticas Big-$O$** ($O(n^2)$ por `pop(0)`, búsquedas lineales en bucles o concatenación cuadrática).
* **🔴 Sombrero Rojo:** Experiencia de desarrollo (DX), ergonomía a las 3:00 AM, **detección de confusión léxica de variables** (`rapidfuzz` Levenshtein), índice de saturación visual y filtro anti-sobreingeniería **Ponytail** (Escalera de la Pereza y Regla de los Tres Golpes).
* **🔵 Sombrero Azul:** Orquestación en **Grafo Dialéctico Cíclico** (`langgraph`), bucle de reversión ante riesgos críticos, telemetría estructurada **OpenTelemetry Spans**, veto de simplicidad Ponytail y parche unificado real (*Unified Diff* con `difflib`).

### Filosofía Agent-Native: Sin dependencia de APIs externas

A diferencia de servidores que encapsulan llamadas fijas a modelos de nube (*antipatrón LLM Sandwich*), `six-hats` está diseñado como un **sustrato analítico determinista**:
1. **Cero configuración de claves:** No requiere `GEMINI_API_KEY` ni configuraciones de facturación de terceros.
2. **Tu modelo favorito al mando:** La inteligencia la aporta el modelo anfitrión con el que interactúas en tu entorno (Antigravity, Claude Desktop, Cursor, Ollama o ChatGPT).
3. **Prompts MCP Oficiales:** Expone primitivas nativas de *Prompts* de MCP (`@app.prompt()`) y directrices cognitivas estructuradas (`agent_guidance`) para que la IA anfitriona ejerza los roles de De Bono con la máxima precisión matemática y contextual.

---

## 2. Arquitectura del sistema y flujo en DAG

```text
                    ┌─────────────────────────┐
                    │  Sombrero Azul (Leader) │
                    │    Orquestador / DAG    │
                    └────────────┬────────────┘
                                 │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
 ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
 │   Blanco     │          │    Verde     │          │     Rojo     │
 │ Contexto/AST │          │  Ideación/   │          │  DX/Legibi-  │
 │  y Métricas  │          │ Alternativas │          │    lidad     │
 └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
           ┌──────────────┐                ┌──────────────┐
           │   Amarillo   │                │    Negro     │
           │ Viabilidad y │                │ Vulnerabili- │
           │  Rendimiento │                │ dades / Bugs │
           └──────────────┘                └──────────────┘
```

1. **Entrada:** Archivo de código fuente (Python, TypeScript, Go o Rust), diff unificado de Git o requerimiento de arquitectura.
2. **Fase 1 (Datos fehacientes):** El Sombrero Blanco extrae el árbol sintáctico con `tree-sitter` o `ast`, calculando complejidad ciclomática, cognitiva, índice de mantenibilidad y dependencias.
3. **Fase 2 (Exploración creativa):** El Sombrero Verde concibe alternativas paradigmáticas (funcional inmutable, reactivo basado en eventos o estructuras zero-copy).
4. **Fase 3 (Crítica paralela concurrente):**
   - El Sombrero Negro audita riesgos de inyección, credenciales expuestas, recursión y denegación de servicio.
   - El Sombrero Amarillo proyecta ganancias de throughput y modernización idiomática.
   - El Sombrero Rojo evalúa la fatiga cognitiva y aplica las reglas Ponytail contra la sobreingeniería (cálculo de *bloat score* y líneas redundantes).
5. **Fase 4 (Síntesis y consenso):** El Sombrero Azul resuelve contradicciones, aplica el veto Ponytail si el *bloat score* supera el umbral, genera el dictamen ejecutivo y sintetiza el parche de código unificado.

---

## 3. Instalación y configuración

### Instalación local con `uv`

```bash
# Crear entorno virtual e instalar en modo editable con herramientas de desarrollo
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Ejecución de la suite de pruebas

```bash
.venv/bin/pytest tests/ -v
```

---

## 4. Soporte políglota universal con Tree-sitter

El analizador sintáctico del Sombrero Blanco detecta automáticamente el lenguaje según la extensión y el contenido:

| Lenguaje | Extensiones | Parser Primario | Métricas Extraídas |
| :--- | :--- | :--- | :--- |
| **Python** | `.py` | `tree-sitter-python` / `ast` nativo | Funciones, clases, imports, complejidad McCabe y SonarSource |
| **TypeScript** | `.ts`, `.tsx` | `tree-sitter-typescript` | Funciones, clases, interfaces, imports y ramificaciones lógicas |
| **JavaScript** | `.js`, `.jsx`, `.mjs` | `tree-sitter-javascript` | Funciones, clases, módulos exportados y complejidad de control |
| **Go** | `.go` | `tree-sitter-go` | Funciones, structs, imports de paquetes y ramas `if`/`for`/`switch` |
| **Rust** | `.rs` | `tree-sitter-rust` | Funciones `fn`, `struct`, `enum`, módulos `use` y expresiones de control |

---

## 5. Uso de la interfaz de línea de comandos (CLI)

El comando `six-hats` (o su alias `hats`) ofrece herramientas enriquecidas con tablas de terminal, paneles coloreados y modos de integración continua:

### Revisión completa de un archivo

```bash
six-hats review ruta/al/archivo.py
six-hats review backend/handler.go
six-hats review frontend/App.tsx
```

### Revisión del `git diff` activo del repositorio

```bash
six-hats review --git-diff
```

### Auditoría de sobreingeniería Ponytail (*Escalera de la Pereza*)

Audita un archivo para detectar código redundante, fábricas innecesarias, envoltorios vacíos y violaciones del principio YAGNI:

```bash
six-hats ponytail ruta/al/archivo.py
six-hats ponytail ruta/al/archivo.py --json
```

### Debate dialéctico sobre una propuesta arquitectónica

```bash
six-hats debate "Migrar el pipeline de ingesta a Kafka distribuido"
```

### Iniciar el servidor MCP en modo STDIO

```bash
six-hats mcp
```

---

## 6. Integración en CI/CD y compuertas de calidad

`six-hats` está preparado para integrarse en flujos de trabajo de GitHub Actions, GitLab CI o pre-commit hooks:

### Salida estructurada JSON

```bash
six-hats review src/main.py --json
```

### Exportación a estándar OASIS SARIF v2.1.0

Genera informes SARIF compatibles con GitHub Code Scanning, GitLab SAST y Azure DevOps:

```bash
six-hats review src/main.py --sarif report.sarif
```

### Compuertas de calidad con `--fail-on`

Detiene la ejecución del pipeline con código de retorno `1` si se identifican riesgos de severidad igual o superior a la indicada:

```bash
# Falla si hay vulnerabilidades críticas de seguridad o fallos estructurales
six-hats review src/main.py --fail-on critical

# Falla si hay riesgos altos (complejidad ciclomática excesiva, race conditions, inyecciones)
six-hats review src/main.py --fail-on high

# Falla si el código presenta sobreingeniería severa según Ponytail
six-hats review src/main.py --fail-on bloat
```

### Configuración con `pre-commit`

Agrega el gancho a tu `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: six-hats-review
        name: Six Hats Code Review
        entry: six-hats review --fail-on high
        language: system
        files: \.(py|ts|tsx|js|jsx|go|rs)$
      - id: six-hats-ponytail
        name: Six Hats Ponytail Bloat Auditor
        entry: six-hats ponytail
        language: system
        files: \.(py|ts|tsx|js|jsx|go|rs)$
```

---

## 7. Integración con Antigravity IDE y clientes MCP

En `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "six-hats": {
      "command": "/home/pablo/Escritorio/SIX HATS/.venv/bin/six-hats",
      "args": ["mcp"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "/home/pablo/Escritorio/SIX HATS/src"
      }
    }
  }
}
```

### Herramientas MCP expuestas

* **`six_hats_review`:** Ejecuta el ciclo completo del DAG sobre un diff o archivo políglota, retornando telemetría de AST, propuestas del Sombrero Verde, auditoría del Sombrero Negro, beneficios del Sombrero Amarillo, evaluación DX/Ponytail del Sombrero Rojo y veredicto con parche unificado y directrices (`agent_guidance`) para la IA anfitriona.
* **`six_hats_debate`:** Lanza una confrontación dialéctica entre el Sombrero Negro y el Sombrero Verde moderada por el Sombrero Azul sobre una propuesta técnica.
* **`six_hats_quick_check`:** Análisis expedito sobre la tríada crítica: Blanco (Hechos), Negro (Riesgos) y Amarillo (Valor).
* **`six_hats_ponytail_audit`:** Auditoría estricta contra la Escalera de la Pereza de Ponytail para detectar sobreingeniería y código superfluo.

### Prompts MCP Oficiales expuestos

El servidor implementa primitivas nativas de *Prompts* de MCP (`@app.prompt()`), disponibles en cualquier cliente compatible:

1. **`six_hats_deliberation`:** Protocolo maestro de deliberación secuencial y paralela con los Seis Sombreros.
2. **`hat_green_creative`:** Protocolo para pensamiento lateral, inversión de supuestos y alternativas paradigmáticas.
3. **`hat_black_adversarial`:** Protocolo para auditoría destructiva, análisis de límites y vector de ataque.
4. **`hat_blue_synthesis`:** Protocolo de mediación dialéctica, veto Ponytail y síntesis de parche unificado.
5. **`six_hats_debate`:** Debate dialéctico formal entre Sombrero Negro y Verde moderado por Sombrero Azul.

---

## 8. Subagentes para Antigravity y Entornos de Desarrollo

El directorio [`subagents/`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/) contiene las especificaciones formales de roles listas para ser instanciadas como subagentes autónomos:

* [`subagents/green_hat.md`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/green_hat.md): Especialista en pensamiento lateral e innovación.
* [`subagents/black_hat.md`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/black_hat.md): Auditor adversarial de seguridad y resiliencia.
* [`subagents/red_hat.md`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/red_hat.md): Auditor de ergonomía a las 3:00 AM y veto Ponytail.
* [`subagents/blue_hat.md`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/blue_hat.md): Orquestador, mediador de compromisos y generador de parches.
* [`subagents/orchestrator.md`](file:///home/pablo/Escritorio/SIX%20HATS/subagents/orchestrator.md): Coordinador de la sesión multi-agente en DAG.
