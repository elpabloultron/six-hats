"""Conector e integrador de grafos de conocimiento de código para Six Hats.

Permite enriquecer la deliberación con la topología de la base de código.
Consume grafos generados por 'graphify' (graphify-out/graph.json) cuando existen,
o genera un subgrafo estructural ligero basado en AST nativo de Python.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Set


def inspect_graphify_output(base_dir: Path | str | None = None) -> Dict[str, Any] | None:
    """Busca y extrae telemetría estructural del directorio graphify-out si existe."""
    root = Path(base_dir) if base_dir else Path.cwd()

    # Rutas típicas generadas por graphify
    candidates = [
        root / "graphify-out" / "graph.json",
        root.parent / "graphify-out" / "graph.json",
        root / "graphify-out" / ".graphify_analysis.json",
    ]

    graph_file = None
    for cand in candidates:
        if cand.exists():
            graph_file = cand
            break

    if not graph_file:
        return None

    try:
        raw_data = json.loads(graph_file.read_text(encoding="utf-8"))
        god_nodes: List[str] = []
        communities: List[str] = []

        if "nodes" in raw_data and "edges" in raw_data:
            # Formato directo de graph.json
            nodes = raw_data.get("nodes", [])
            edges = raw_data.get("edges", [])

            # Calcular grados de centralidad (in-degree + out-degree)
            degree_map: Dict[str, int] = {}
            for edge in edges:
                src = edge.get("source") or edge.get("from")
                tgt = edge.get("target") or edge.get("to")
                if src:
                    degree_map[src] = degree_map.get(src, 0) + 1
                if tgt:
                    degree_map[tgt] = degree_map.get(tgt, 0) + 1

            # Los 5 nodos con mayor acoplamiento
            sorted_nodes = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)
            god_nodes = [f"{n} ({deg} conexiones)" for n, deg in sorted_nodes[:5]]

            # Extraer comunidades si vienen etiquetadas en nodos
            comm_set: Set[str] = set()
            for n in nodes:
                cname = n.get("community_name") or n.get("community")
                if cname:
                    comm_set.add(str(cname))
            communities = sorted(list(comm_set))

        elif "gods" in raw_data:
            # Formato de .graphify_analysis.json
            god_nodes = raw_data.get("gods", [])[:5]
            comms_raw = raw_data.get("communities", {})
            communities = [f"Comunidad {k}" for k in comms_raw.keys()]

        return {
            "source": "Graphify Knowledge Graph",
            "is_graphify": True,
            "path": str(graph_file),
            "god_nodes": god_nodes,
            "communities": communities,
            "total_nodes": len(raw_data.get("nodes", [])),
            "total_edges": len(raw_data.get("edges", [])),
        }
    except Exception:
        return None


def extract_ast_subgraph(code_content: str) -> Dict[str, Any]:
    """Genera un subgrafo ligero de dependencias locales a partir del AST de Python."""
    if not code_content.strip():
        return {
            "source": "AST Fallback",
            "is_graphify": False,
            "god_nodes": [],
            "communities": [],
            "total_nodes": 0,
            "total_edges": 0,
        }

    try:
        tree = ast.parse(code_content)
    except SyntaxError:
        return {
            "source": "AST Fallback (Syntax Error)",
            "is_graphify": False,
            "god_nodes": [],
            "communities": [],
            "total_nodes": 0,
            "total_edges": 0,
        }

    definitions: List[str] = []
    calls: Dict[str, int] = {}
    imports: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions.append(f"def {node.name}")
        elif isinstance(node, ast.ClassDef):
            definitions.append(f"class {node.name}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls[node.func.id] = calls.get(node.func.id, 0) + 1
            elif isinstance(node.func, ast.Attribute):
                calls[node.func.attr] = calls.get(node.func.attr, 0) + 1
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append(mod)

    # Identificar símbolos más invocados como puntos centrales
    sorted_calls = sorted(calls.items(), key=lambda x: x[1], reverse=True)
    top_calls = [f"{name}() ({count} llamadas)" for name, count in sorted_calls[:5]]

    return {
        "source": "AST Nativo (Subgrafo Estructural)",
        "is_graphify": False,
        "god_nodes": top_calls,
        "communities": [f"Módulo ({len(definitions)} definiciones)", f"Dependencias ({len(imports)} imports)"],
        "definitions": definitions,
        "imports": imports,
        "total_nodes": len(definitions) + len(imports),
        "total_edges": sum(calls.values()),
    }


def detect_codebase_graph(
    base_dir: Path | str | None = None,
    code_content: str | None = None,
) -> Dict[str, Any]:
    """Orquestador: intenta usar Graphify primero; de no existir, calcula subgrafo AST."""
    graphify_res = inspect_graphify_output(base_dir)
    if graphify_res:
        return graphify_res

    return extract_ast_subgraph(code_content or "")
