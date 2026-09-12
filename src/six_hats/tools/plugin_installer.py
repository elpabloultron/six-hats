import json
import os
import sys
from pathlib import Path
from typing import Any


def get_server_definition(method: str = "uvx") -> dict[str, Any]:
    """Genera la definición del servidor MCP según el método ('uvx' o 'local')."""
    if method == "local":
        # Usar el ejecutable de python actual o 'six-hats'
        python_bin = sys.executable
        venv_bin = Path(python_bin).parent / "six-hats"
        cmd = str(venv_bin) if venv_bin.exists() else "six-hats"
        return {
            "command": cmd,
            "args": ["mcp"],
            "env": {
                "PYTHONIOENCODING": "utf-8",
            },
        }
    else:
        # Método 'uvx' oficial desde PyPI
        return {
            "command": "uvx",
            "args": [
                "six-hats",
                "mcp",
            ],
        }


def merge_mcp_config(target_file: Path, server_name: str, server_def: dict[str, Any], dry_run: bool = False) -> tuple[str, dict[str, Any]]:
    """Carga, actualiza de forma idempotente y guarda la configuración MCP."""
    data: dict[str, Any] = {}
    action = "created"

    if target_file.exists():
        action = "updated"
        try:
            content = target_file.read_text(encoding="utf-8")
            data = json.loads(content) if content.strip() else {}
        except Exception:
            data = {}

    if "mcpServers" not in data:
        data["mcpServers"] = {}

    data["mcpServers"][server_name] = server_def

    if not dry_run:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return action, data


def install_plugin(
    target: str = "all",
    scope: str = "project",
    method: str = "uvx",
    cwd: Path | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Instala o registra six-hats como plugin/servidor MCP en el cliente indicado.

    Args:
        target: 'claude', 'cursor', 'vscode', 'antigravity' o 'all'.
        scope: 'project' (en la carpeta de trabajo) o 'global' (en el directorio home).
        method: 'uvx' (instalación remota con git) o 'local' (entorno python actual).
        cwd: Directorio base de trabajo (por defecto Path.cwd()).
        dry_run: Si es True, no escribe en disco.

    Returns:
        Lista de resultados con target, ruta del archivo, acción y configuración resultante.
    """
    base_dir = cwd or Path.cwd()
    home_dir = Path.home()
    server_def = get_server_definition(method)
    results: list[dict[str, Any]] = []

    targets_to_run = ["claude", "cursor", "vscode"] if target == "all" else [target.lower()]

    for t in targets_to_run:
        if t == "claude":
            if scope == "global":
                target_path = home_dir / ".claude.json"
            else:
                target_path = base_dir / ".mcp.json"
        elif t == "cursor":
            if scope == "global":
                target_path = home_dir / ".cursor" / "mcp.json"
            else:
                target_path = base_dir / ".cursor" / "mcp.json"
        elif t == "vscode":
            if scope == "global":
                target_path = home_dir / ".config" / "Code" / "User" / "mcp.json"
            else:
                target_path = base_dir / ".vscode" / "mcp.json"
        elif t == "antigravity":
            target_path = home_dir / ".gemini" / "antigravity" / "mcp_config.json"
        else:
            continue

        action, data = merge_mcp_config(
            target_file=target_path,
            server_name="six-hats",
            server_def=server_def,
            dry_run=dry_run,
        )

        results.append({
            "target": t,
            "scope": scope,
            "method": method,
            "filepath": str(target_path),
            "action": f"dry_run ({action})" if dry_run else action,
            "config": data,
        })

    return results
