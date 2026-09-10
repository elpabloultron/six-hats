import asyncio
import json
from typing import Any
from six_hats.mcp_server import app


def get_raw_tools_sync() -> list[Any]:
    """Obtiene la lista de herramientas registradas en el servidor MCP de forma sincrónica."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, app.list_tools()).result()
    else:
        return asyncio.run(app.list_tools())


def export_openai_tools() -> list[dict[str, Any]]:
    """Exporta las herramientas en el formato estándar OpenAI Function Calling / Codex."""
    raw_tools = get_raw_tools_sync()
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
            },
        }
        for t in raw_tools
    ]


def export_claude_tools() -> list[dict[str, Any]]:
    """Exporta las herramientas en el formato nativo de Anthropic Claude Messages API."""
    raw_tools = get_raw_tools_sync()
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
        }
        for t in raw_tools
    ]


def export_hermes_tools() -> list[dict[str, Any]]:
    """Exporta las herramientas en el formato compatible con Nous Hermes (ChatML Tool Calling)."""
    return export_openai_tools()


def export_mcp_tools() -> list[dict[str, Any]]:
    """Exporta las herramientas en el formato estándar Model Context Protocol (inputSchema)."""
    raw_tools = get_raw_tools_sync()
    return [
        {
            "name": t.name,
            "description": t.description,
            "inputSchema": t.input_schema,
        }
        for t in raw_tools
    ]


def build_hermes_chatml_block() -> str:
    """Genera el bloque textual <tools>...</tools> para inyectar en el system prompt de modelos Hermes."""
    tools = export_hermes_tools()
    tools_str = json.dumps(tools, indent=2, ensure_ascii=False)
    return f"<tools>\n{tools_str}\n</tools>"


def export_tools_by_format(format_name: str) -> str:
    """Exporta las herramientas según el formato solicitado ('openai', 'hermes', 'claude', 'mcp')."""
    fmt = format_name.lower().strip()
    if fmt in ("openai", "codex"):
        return json.dumps(export_openai_tools(), indent=2, ensure_ascii=False)
    elif fmt == "claude":
        return json.dumps(export_claude_tools(), indent=2, ensure_ascii=False)
    elif fmt == "hermes":
        return json.dumps(export_hermes_tools(), indent=2, ensure_ascii=False)
    elif fmt == "hermes-chatml":
        return build_hermes_chatml_block()
    elif fmt == "mcp":
        return json.dumps(export_mcp_tools(), indent=2, ensure_ascii=False)
    else:
        raise ValueError(
            f"Formato '{format_name}' no reconocido. Formatos válidos: 'openai', 'hermes', 'hermes-chatml', 'claude', 'mcp'."
        )
