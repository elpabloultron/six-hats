# Guía de Integración Multi-Agente y Multi-Plataforma para Six Hats

Este directorio contiene las especificaciones y ejemplos para integrar **`six-hats`** en cualquier entorno o framework de agentes de inteligencia artificial.

---

## 1. Claude Code (CLI de Anthropic)

Claude Code detecta automáticamente los servidores MCP configurados en el proyecto a través del archivo [`.mcp.json`](file:///home/pablo/Escritorio/SIX%20HATS/.mcp.json) o mediante el CLI oficial.

### Instalación en un solo comando
```bash
claude mcp add six-hats uvx --from git+https://github.com/elpabloultron/six-hats.git six-hats mcp
```

### Autodescubrimiento en el espacio de trabajo
Copia o genera el archivo `.mcp.json` en la raíz de tu proyecto:
```bash
six-hats plugin install claude --scope project
```

El archivo [`CLAUDE.md`](file:///home/pablo/Escritorio/SIX%20HATS/CLAUDE.md) en la raíz instruye a Claude Code a razonar metódicamente con las perspectivas de los Seis Sombreros e invocar las herramientas analíticas.

---

## 2. Cursor IDE y Visual Studio Code

### Configuración con el CLI de Six Hats
```bash
# Para el proyecto actual
six-hats plugin install cursor --scope project
six-hats plugin install vscode --scope project

# O para todos los clientes en una sola ejecución:
six-hats plugin install all --scope project
```

---

## 3. Nous Hermes 2 y 3 (ChatML Tool Calling)

Los modelos de la familia **Hermes** de Nous Research utilizan el formato ChatML con bloques `<tools>` y `<tool_call>`.

### Archivos provistos
- [`hermes_tools.json`](file:///home/pablo/Escritorio/SIX%20HATS/integrations/hermes/hermes_tools.json): Esquema precompilado de las herramientas.
- [`system_prompt.txt`](file:///home/pablo/Escritorio/SIX%20HATS/integrations/hermes/system_prompt.txt): Plantilla de system prompt que inyecta las herramientas y las reglas metodológicas de los 6 Sombreros.
- [`hermes_runner_example.py`](file:///home/pablo/Escritorio/SIX%20HATS/integrations/hermes/hermes_runner_example.py): Despachador de llamadas en Python.

---

## 4. OpenAI Codex / Assistants API / LiteLLM

Compatible con cualquier modelo o plataforma que acepte la especificación estándar de `tools: [{"type": "function", ...}]`.

### Exportación dinámica
```bash
six-hats export-tools --format openai --output mi_esquema.json
```

Ver ejemplo funcional en [`agent_runner_example.py`](file:///home/pablo/Escritorio/SIX%20HATS/integrations/openai_codex/agent_runner_example.py).

---

## 5. Orquestadores Multi-Agente (LangGraph, CrewAI, AutoGen)

En arquitecturas multi-agente, `six-hats` puede operar de dos maneras complementarias:

1. **Como Agente Crítico de Aprobación (Gatekeeper / Deliberator):**
   Un nodo de control que evalúa el código producido por agentes generadores, calcula la sobreingeniería (Ponytail bloat score) y veta o aprueba el avance.
2. **Como Caja de Herramientas (*Toolbox*):**
   Se asignan `six_hats_review`, `six_hats_debate` o `six_hats_ponytail_audit` a los agentes especializados de revisión y seguridad.

Revisa la implementación en [`langgraph_six_hats.py`](file:///home/pablo/Escritorio/SIX%20HATS/integrations/multi_agent/langgraph_six_hats.py).
