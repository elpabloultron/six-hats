import pytest
import json
import asyncio
from six_hats.core.models import (
    WhiteHatData,
    BlackHatFinding,
    YellowHatBenefit,
    GreenHatProposal,
    RedHatAssessment,
    SixHatsConsensus,
)
from six_hats.tools.ast_extractor import extract_ast_data
from six_hats.tools.git_utils import get_file_diff_stats
from six_hats.tools.security_scanner import scan_security_vulnerabilities
from six_hats.tools.cognitive_metrics import calculate_cognitive_complexity, calculate_maintainability_index
from six_hats.tools.ponytail_rules import audit_ponytail
from six_hats.core.patterns import get_divergent_proposals
from six_hats.core.orchestrator import SixHatsOrchestrator
from six_hats.mcp_server import app


SAMPLE_PYTHON_CODE = """
import os
import sys
from pathlib import Path

def procesar_archivo(ruta: str):
    p = Path(ruta)
    if not p.exists():
        return None
    contenido = p.read_text(encoding="utf-8")
    for linea in contenido.splitlines():
        if "error" in linea:
            print("Error detectado")
    return True
"""

SAMPLE_DANGEROUS_CODE = """
import pickle
import subprocess

def peligroso(comando, payload):
    eval(comando)
    pickle.loads(payload)
    subprocess.run("ls -la", shell=True)
    api_key = "AKIA1234567890ABCDEF"
    try:
        resultado = 1 / 0
    except:
        pass
"""

SAMPLE_OVERENGINEERED_CODE = """
class DataFetcherSingleMethod:
    def fetch(self, url: str):
        return url.strip()

class EmptySpeculativeClass:
    pass

def verbose_collector(items):
    res = []
    for item in items:
        res.append(item.upper())
    return res

def redundant_wrapper(a, b):
    return sum_two(a, b)

def read_custom(filepath):
    with open(filepath, "r") as f:
        data = f.read()
    return data
"""


def test_models_validation():
    """Verifica la validación e integridad de los modelos Pydantic enriquecidos."""
    white = WhiteHatData(
        symbols_affected=["def test"],
        cyclomatic_complexity=2,
        cognitive_complexity=1,
        maintainability_index=88.5,
        lines_added=10,
        lines_deleted=2,
        test_coverage_pct=85.5,
        dependencies=["os", "sys"],
    )
    assert white.cyclomatic_complexity == 2
    assert white.cognitive_complexity == 1
    assert white.maintainability_index == 88.5

    black = BlackHatFinding(
        severity="HIGH",
        risk_type="Deadlock",
        location="worker.py:45",
        description="Falta de timeout",
        cwe_owasp_id="CWE-400",
    )
    assert black.cwe_owasp_id == "CWE-400"


def test_ast_extractor_with_cognitive_metrics():
    """Prueba la extracción de AST, complejidad ciclomática y complejidad cognitiva."""
    data = extract_ast_data(SAMPLE_PYTHON_CODE)
    assert "def procesar_archivo" in data.symbols_affected
    assert "pathlib" in data.dependencies
    assert data.cyclomatic_complexity >= 3
    assert data.cognitive_complexity >= 2
    assert 0.0 <= data.maintainability_index <= 100.0


def test_cognitive_complexity_nesting_penalty():
    """Prueba que el anidamiento profundo incremente severamente la complejidad cognitiva de SonarSource."""
    flat_code = """
def flat(a, b):
    if a:
        return 1
    if b:
        return 2
    return 0
"""
    nested_code = """
def nested(a, b, c):
    if a:
        if b:
            if c:
                return True
    return False
"""
    comp_flat = calculate_cognitive_complexity(flat_code)
    comp_nested = calculate_cognitive_complexity(nested_code)

    # El código anidado debe tener una complejidad cognitiva significativamente mayor por penalización
    assert comp_nested > comp_flat


def test_security_scanner_rules():
    """Prueba la detección de eval, pickle, shell=True, secretos AWS y except genérico."""
    findings = scan_security_vulnerabilities(SAMPLE_DANGEROUS_CODE)
    types = [f.risk_type for f in findings]
    severities = [f.severity for f in findings]

    assert any("Inyección de Código" in t for t in types)
    assert any("Deserialización Insegura" in t for t in types)
    assert any("Inyección de Comandos" in t for t in types)
    assert any("Exposición de Credenciales" in t for t in types)
    assert any("Supresión Silenciosa" in t for t in types)
    assert "CRITICAL" in severities


def test_ponytail_rules_ladder_of_laziness():
    """Prueba la detección de los peldaños de Ponytail (clases de método único, bucles verbosos, stdlib)."""
    report = audit_ponytail(SAMPLE_OVERENGINEERED_CODE)

    assert report.bloat_score > 20.0
    violations = [v.name for v in report.violations]
    assert any("Clase de Método Único" in v for v in violations)
    assert any("Clase Vacía" in v for v in violations)
    assert any("Bucle Imperativo Verboso" in v for v in violations)
    assert any("Función Wrapper Redundante" in v for v in violations)
    assert any("pathlib.Path.read_text" in v for v in violations)
    assert report.estimated_lines_reducible > 0


def test_green_hat_patterns_catalog():
    """Prueba la obtención de propuestas arquitectónicas divergentes del catálogo."""
    proposals = get_divergent_proposals(task_context="Optimizar latencia extrema y concurrencia")
    assert len(proposals) >= 3
    names = [p.name for p in proposals]
    assert any("Zero-Copy" in n or "Reactor" in n for n in names)


@pytest.mark.asyncio
async def test_orchestrator_full_cycle_with_ponytail_and_security():
    """Prueba el flujo completo del DAG integrando Ponytail, métricas y seguridad."""
    orchestrator = SixHatsOrchestrator()
    result = await orchestrator.run_full_cycle(SAMPLE_PYTHON_CODE, is_diff=False)

    assert result.white.cognitive_complexity >= 1
    assert len(result.green) >= 3
    assert len(result.black) >= 1
    assert result.red.bloat_score >= 0.0
    assert result.consensus.verdict in ("APPROVE", "REQUIRE_CHANGES")


@pytest.mark.asyncio
async def test_orchestrator_ponytail_veto_on_bloat():
    """Prueba que código con sobreingeniería excesiva active el veto de Ponytail."""
    orchestrator = SixHatsOrchestrator()
    result = await orchestrator.run_full_cycle(SAMPLE_OVERENGINEERED_CODE, is_diff=False)

    assert result.red.bloat_score > 20.0
    assert len(result.red.ladder_violations) > 0


@pytest.mark.asyncio
async def test_mcp_server_tools_including_ponytail():
    """Prueba que el servidor MCP exponga y ejecute six_hats_ponytail_audit."""
    tools = await app.list_tools()
    tool_names = [t.name for t in tools]
    assert "six_hats_review" in tool_names
    assert "six_hats_debate" in tool_names
    assert "six_hats_quick_check" in tool_names
    assert "six_hats_ponytail_audit" in tool_names

    # Llamada a six_hats_ponytail_audit
    res = await app.call_tool("six_hats_ponytail_audit", {"code": SAMPLE_OVERENGINEERED_CODE, "threshold": 20.0})
    assert not res.is_error
    assert res.content
    data = json.loads(res.content[0].text)
    assert "bloat_score" in data
    assert "violations" in data
    assert len(data["violations"]) >= 3


def test_real_diff_patch_generation():
    """Fase 1: Prueba que el generador de parches produzca un Unified Diff aplicable."""
    from six_hats.tools.diff_generator import generate_real_patch

    patch = generate_real_patch(
        original_code=SAMPLE_DANGEROUS_CODE,
        filepath="peligro.py",
        applied_mitigations=["Deshabilitar eval()"],
    )
    assert patch != ""
    assert "--- a/peligro.py" in patch
    assert "+++ b/peligro.py" in patch
    assert "eval" in patch


def test_sarif_export_schema():
    """Fase 2: Prueba la generación de informe SARIF v2.1.0 para CI/CD."""
    from six_hats.tools.sarif_exporter import build_sarif_report

    orchestrator = SixHatsOrchestrator()
    result = asyncio.run(orchestrator.run_full_cycle(SAMPLE_DANGEROUS_CODE, is_diff=False))
    sarif = build_sarif_report(result, filepath="peligro.py")

    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "six-hats"
    assert len(run["results"]) >= 1


def test_tree_sitter_polyglot_typescript():
    """Fase 3: Prueba el análisis sintáctico de TypeScript con Tree-sitter."""
    from six_hats.tools.tree_sitter_engine import analyze_tree_sitter

    ts_code = """
import { useState } from 'react';

interface User {
    id: number;
    name: string;
}

export function processUser(user: User): boolean {
    if (user.id > 0 && user.name.length > 0) {
        for (let i = 0; i < 5; i++) {
            console.log(i);
        }
        return true;
    }
    return false;
}
"""
    result = analyze_tree_sitter(ts_code, filename="user.ts")
    assert result is not None
    symbols, cyclomatic, cognitive, deps = result

    assert any("User" in s for s in symbols)
    assert any("processUser" in s for s in symbols)
    assert cyclomatic >= 3
    assert cognitive >= 2
    assert "react" in deps


def test_tree_sitter_polyglot_go():
    """Fase 3: Prueba el análisis sintáctico de Go con Tree-sitter."""
    from six_hats.tools.tree_sitter_engine import analyze_tree_sitter

    go_code = """
package main

import "fmt"

type Server struct {
    port int
}

func (s *Server) Start() error {
    if s.port <= 0 {
        return fmt.Errorf("invalid port")
    }
    return nil
}
"""
    result = analyze_tree_sitter(go_code, filename="server.go")
    assert result is not None
    symbols, cyclomatic, cognitive, deps = result

    assert any("Start" in s for s in symbols)
    assert any("Server" in s for s in symbols)
    assert cyclomatic >= 2
    assert "fmt" in deps


def test_tree_sitter_polyglot_rust():
    """Fase 3: Prueba el análisis sintáctico de Rust con Tree-sitter."""
    from six_hats.tools.tree_sitter_engine import analyze_tree_sitter

    rs_code = """
use std::io;

struct Worker {
    id: u32,
}

impl Worker {
    fn run(&self) -> io::Result<()> {
        if self.id > 0 {
            Ok(())
        } else {
            Err(io::Error::new(io::ErrorKind::Other, "err"))
        }
    }
}
"""
    result = analyze_tree_sitter(rs_code, filename="worker.rs")
    assert result is not None
    symbols, cyclomatic, cognitive, deps = result

    assert any("Worker" in s for s in symbols)
    assert any("run" in s for s in symbols)
    assert cyclomatic >= 2
    assert "std" in deps


@pytest.mark.asyncio
async def test_mcp_server_prompts_agent_native():
    """Fase 1 (Agent-Native): Prueba que el servidor MCP exponga y resuelva los prompts oficiales."""
    prompts = await app.list_prompts()
    prompt_names = [p.name for p in prompts]
    assert "six_hats_deliberation" in prompt_names
    assert "hat_green_creative" in prompt_names
    assert "hat_black_adversarial" in prompt_names
    assert "hat_blue_synthesis" in prompt_names
    assert "six_hats_debate" in prompt_names

    # Obtención y validación de contenido de prompt
    res = await app.get_prompt("hat_green_creative", {"task_context": "Optimizar pipeline de eventos"})
    assert res.messages
    text_content = res.messages[0].content.text
    assert "SOMBRERO VERDE" in text_content
    assert "Pensamiento Lateral" in text_content
    assert "Optimizar pipeline de eventos" in text_content


@pytest.mark.asyncio
async def test_consensus_agent_guidance_included():
    """Fase 1 (Agent-Native): Prueba que SixHatsConsensus incluya las directrices para la IA anfitriona."""
    orchestrator = SixHatsOrchestrator()
    result = await orchestrator.run_full_cycle(SAMPLE_PYTHON_CODE, is_diff=False)
    assert result.consensus.agent_guidance is not None
    assert "MANDATO PARA LA IA ANFITRIONA (SOMBRERO AZUL)" in result.consensus.agent_guidance
    assert "Telemetría Forense" in result.consensus.agent_guidance


def test_shannon_entropy_calculation():
    """Sombrero Negro: Prueba el cálculo de entropía de Shannon (TruffleHog)."""
    from six_hats.tools.security_scanner import calculate_shannon_entropy

    low_entropy = calculate_shannon_entropy("aaaaaaaaaaaaaaaaaaaa")
    assert low_entropy < 1.0

    # Token aleatorio con caracteres alfanuméricos variados
    high_entropy = calculate_shannon_entropy("dGhpcy1pcy1hLXN1cGVyLXJhbmRvbS1zZWNyZXQtdG9rZW4tMTIzNDU2")
    assert high_entropy > 4.0


def test_property_invariants_hypothesis():
    """Sombrero Negro: Prueba la generación de invariantes de propiedad y fuzzing (Hypothesis)."""
    from six_hats.tools.security_scanner import generate_property_invariants

    sample_code = "def process_user_query(text: str, limit: int, items: list): pass"
    invariants = generate_property_invariants(sample_code)

    assert len(invariants) >= 3
    assert any("Fuzzing de Cadenas" in inv for inv in invariants)
    assert any("Fuzzing Numérico" in inv for inv in invariants)
    assert any("Invariante de Colecciones" in inv for inv in invariants)


def test_performance_analyzer_big_o():
    """Sombrero Amarillo: Prueba la detección de trampas de rendimiento Big-O O(n²)."""
    from six_hats.tools.performance_analyzer import analyze_performance_bottlenecks

    sample_slow_code = """
def process_data(items):
    res = ""
    for item in items:
        if item in items:
            items.pop(0)
            res += str(item)
    return res
"""
    bottlenecks = analyze_performance_bottlenecks(sample_slow_code)
    assert len(bottlenecks) >= 2
    types = [b["type"] for b in bottlenecks]
    assert any("pop(0)" in t for t in types)
    assert any("Búsqueda Lineal" in t or "Concatenación" in t for t in types)


def test_lexical_confusion_levenshtein():
    """Sombrero Rojo: Prueba la detección de confusión léxica de variables a las 3:00 AM (RapidFuzz)."""
    from six_hats.tools.ponytail_rules import detect_lexical_confusion

    confusing_code = """
def update_profile(user_id: int, user_idx: int, request_data: dict, requests_data: dict):
    if user_id > 0:
        return user_idx + len(request_data)
"""
    warnings = detect_lexical_confusion(confusing_code)
    assert len(warnings) >= 1
    assert any("user_id" in w and "user_idx" in w for w in warnings)


@pytest.mark.asyncio
async def test_cyclic_feedback_loop_on_critical():
    """Sombrero Azul / LangGraph: Prueba que el grafo dialéctico active el bucle de reversión ante riesgos críticos."""
    orchestrator = SixHatsOrchestrator()
    # SAMPLE_DANGEROUS_CODE contiene eval(), que es CRITICAL
    result = await orchestrator.run_full_cycle(SAMPLE_DANGEROUS_CODE, is_diff=False)

    assert result.feedback_loop_count == 1
    assert len(result.deliberation_trace) >= 4
    span_names = [s["span_name"] for s in result.deliberation_trace]
    assert "cyclic_feedback_loopback" in span_names
    assert any("Aislamiento Seguro" in p.name for p in result.green)


def test_git_churn_and_coverage_graceful():
    """Sombrero Blanco: Prueba la degradación graciosa de análisis de Git y cobertura."""
    from six_hats.tools.git_utils import analyze_git_churn, detect_coverage_report

    churn, risk = analyze_git_churn("non_existent_file.xyz")
    assert risk in ("LOW", None)

    cov = detect_coverage_report("non_existent_file.xyz")
    assert cov is None


def test_export_tools_schemas():
    """Fase Plugin: Prueba la exportación de esquemas en formatos OpenAI, Claude, Hermes y MCP."""
    from six_hats.tools.exporter import (
        export_openai_tools,
        export_claude_tools,
        export_hermes_tools,
        export_mcp_tools,
        build_hermes_chatml_block,
        export_tools_by_format,
    )

    openai_tools = export_openai_tools()
    assert len(openai_tools) >= 10
    assert all(t["type"] == "function" for t in openai_tools)
    names = [t["function"]["name"] for t in openai_tools]
    assert "six_hats_review" in names
    assert "six_hats_ponytail_audit" in names
    assert "six_hats_white_hat" in names
    assert "six_hats_black_hat" in names
    assert "six_hats_batch_scan" in names

    claude_tools = export_claude_tools()
    assert len(claude_tools) >= 10
    assert all("input_schema" in t for t in claude_tools)

    mcp_tools = export_mcp_tools()
    assert len(mcp_tools) >= 10
    assert all("inputSchema" in t for t in mcp_tools)

    chatml = build_hermes_chatml_block()
    assert chatml.startswith("<tools>\n")
    assert chatml.endswith("</tools>")

    # Formatos por string
    assert "six_hats_review" in export_tools_by_format("openai")
    assert "six_hats_review" in export_tools_by_format("claude")
    assert "six_hats_review" in export_tools_by_format("hermes")
    assert "<tools>" in export_tools_by_format("hermes-chatml")
    assert "inputSchema" in export_tools_by_format("mcp")

    with pytest.raises(ValueError):
        export_tools_by_format("formato_invalido")


def test_plugin_installer_execution(tmp_path):
    """Fase Plugin: Prueba la instalación y merge de configuraciones MCP en Cursor, Claude y VSCode."""
    from six_hats.tools.plugin_installer import install_plugin

    # Prueba simulación (dry_run)
    res_dry = install_plugin("all", scope="project", method="uvx", cwd=tmp_path, dry_run=True)
    assert len(res_dry) == 3
    assert not (tmp_path / ".mcp.json").exists()

    # Prueba escritura real en tmp_path
    res_real = install_plugin("all", scope="project", method="uvx", cwd=tmp_path, dry_run=False)
    assert len(res_real) == 3

    mcp_claude = tmp_path / ".mcp.json"
    mcp_cursor = tmp_path / ".cursor" / "mcp.json"
    mcp_vscode = tmp_path / ".vscode" / "mcp.json"

    assert mcp_claude.exists()
    assert mcp_cursor.exists()
    assert mcp_vscode.exists()

    claude_data = json.loads(mcp_claude.read_text(encoding="utf-8"))
    assert "six-hats" in claude_data["mcpServers"]
    assert claude_data["mcpServers"]["six-hats"]["command"] == "uvx"


def test_cli_plugin_and_export_commands(tmp_path):
    """Fase Plugin: Prueba los subcomandos de CLI 'export-tools' y 'plugin install'."""
    from click.testing import CliRunner
    from six_hats.cli import cli

    runner = CliRunner()

    # Prueba export-tools a stdout
    res_exp = runner.invoke(cli, ["export-tools", "--format", "openai"])
    assert res_exp.exit_code == 0
    assert "six_hats_review" in res_exp.output

    # Prueba export-tools guardando en archivo
    out_file = tmp_path / "custom_tools.json"
    res_save = runner.invoke(cli, ["export-tools", "--format", "claude", "--output", str(out_file)])
    assert res_save.exit_code == 0
    assert out_file.exists()
    assert "six_hats_ponytail_audit" in out_file.read_text(encoding="utf-8")

    # Prueba plugin install --dry-run
    res_plugin = runner.invoke(cli, ["plugin", "install", "claude", "--dry-run"])
    assert res_plugin.exit_code == 0
    assert "Claude" in res_plugin.output
    assert "dry_run" in res_plugin.output


def test_cli_review_with_html_and_sarif(tmp_path):
    """Prueba la invocación de review con exportación combinada de HTML y SARIF."""
    from click.testing import CliRunner
    from six_hats.cli import cli

    sample_file = tmp_path / "calc.py"
    sample_file.write_text("def sumar(a, b): return a + b\n", encoding="utf-8")

    html_out = tmp_path / "report.html"
    sarif_out = tmp_path / "report.sarif"

    runner = CliRunner()
    result = runner.invoke(cli, [
        "review",
        str(sample_file),
        "--html",
        str(html_out),
        "--sarif",
        str(sarif_out),
    ])

    assert result.exit_code == 0
    assert html_out.exists()
    assert sarif_out.exists()
    assert "Dashboard visual HTML exportado" in result.output
    assert "Informe SARIF v2.1.0 exportado" in result.output





