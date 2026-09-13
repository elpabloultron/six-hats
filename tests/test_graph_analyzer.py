"""Pruebas unitarias para el conector e integrador de grafos de código (graph_analyzer)."""

import json
from pathlib import Path
from six_hats.tools.graph_analyzer import (
    extract_ast_subgraph,
    inspect_graphify_output,
    detect_codebase_graph,
)

SAMPLE_CODE = """
import os
from pathlib import Path

class GestorDocumentos:
    def __init__(self, ruta: str):
        self.ruta = ruta

    def leer(self):
        return Path(self.ruta).read_text()

def principal():
    g = GestorDocumentos("doc.txt")
    return g.leer()
"""


def test_extract_ast_subgraph():
    """Prueba la extracción de símbolos, llamadas e imports mediante AST nativo."""
    data = extract_ast_subgraph(SAMPLE_CODE)
    assert not data["is_graphify"]
    assert "AST Nativo" in data["source"]
    assert "class GestorDocumentos" in data["definitions"]
    assert "def principal" in data["definitions"]
    assert "os" in data["imports"]
    assert "pathlib" in data["imports"]
    assert data["total_nodes"] >= 4
    assert data["total_edges"] >= 1


def test_inspect_graphify_output_mock(tmp_path: Path):
    """Prueba la ingesta y extracción de god nodes desde un grafo simulado de Graphify."""
    graphify_dir = tmp_path / "graphify-out"
    graphify_dir.mkdir()
    graph_file = graphify_dir / "graph.json"

    mock_graph = {
        "nodes": [
            {"id": "AuthModule", "community_name": "Autenticación"},
            {"id": "DatabaseService", "community_name": "Persistencia"},
            {"id": "UserRoutes", "community_name": "API"},
        ],
        "edges": [
            {"source": "UserRoutes", "target": "AuthModule"},
            {"source": "UserRoutes", "target": "DatabaseService"},
            {"source": "AuthModule", "target": "DatabaseService"},
        ],
    }
    graph_file.write_text(json.dumps(mock_graph), encoding="utf-8")

    result = inspect_graphify_output(tmp_path)
    assert result is not None
    assert result["is_graphify"] is True
    assert result["source"] == "Graphify Knowledge Graph"
    assert result["total_nodes"] == 3
    assert result["total_edges"] == 3
    assert any("DatabaseService" in n for n in result["god_nodes"])
    assert "Autenticación" in result["communities"]
    assert "Persistencia" in result["communities"]


def test_detect_codebase_graph_fallback():
    """Prueba que detect_codebase_graph realice fallback gracioso a AST si no hay graphify-out."""
    res = detect_codebase_graph(base_dir="/directorio/inexistente", code_content=SAMPLE_CODE)
    assert res is not None
    assert not res["is_graphify"]
    assert "AST Nativo" in res["source"]
    assert len(res["definitions"]) >= 3
