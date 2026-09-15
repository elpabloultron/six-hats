import pytest
import json
from click.testing import CliRunner

from six_hats.agents import (
    HatAgent,
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
    get_agent,
    HAT_AGENTS_REGISTRY,
)
from six_hats.core.models import (
    WhiteHatData,
    GreenHatProposal,
    BlackHatFinding,
    YellowHatBenefit,
    RedHatAssessment,
    SixHatsConsensus,
)
from six_hats.core.orchestrator import SixHatsOrchestrator
from six_hats.cli import cli
from six_hats.mcp_server import (
    six_hats_white_hat,
    six_hats_green_hat,
    six_hats_black_hat,
    six_hats_yellow_hat,
    six_hats_red_hat,
    six_hats_blue_hat,
)

SAMPLE_CLEAN_CODE = """
def sumar(a: int, b: int) -> int:
    \"\"\"Calcula la suma de dos enteros.\"\"\"
    return a + b
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
"""


def test_get_agent_factory():
    """Verifica que la fábrica get_agent devuelva instancias correctas en inglés y español."""
    for en_name, agent_cls in HAT_AGENTS_REGISTRY.items():
        agent = get_agent(en_name)
        assert isinstance(agent, agent_cls)
        assert agent.hat_name == en_name

    es_map = {
        "blanco": WhiteHatAgent,
        "rojo": RedHatAgent,
        "negro": BlackHatAgent,
        "amarillo": YellowHatAgent,
        "verde": GreenHatAgent,
        "azul": BlueHatAgent,
    }
    for es_name, agent_cls in es_map.items():
        agent = get_agent(es_name)
        assert isinstance(agent, agent_cls)

    with pytest.raises(ValueError, match="Sombrero no reconocido"):
        get_agent("purpura")


@pytest.mark.asyncio
async def test_white_hat_agent():
    """Verifica el análisis fáctico y la telemetría del Sombrero Blanco."""
    agent = WhiteHatAgent()
    data = await agent.execute(SAMPLE_CLEAN_CODE, filename="clean.py")
    assert isinstance(data, WhiteHatData)
    assert data.cyclomatic_complexity >= 1
    assert "def sumar" in data.symbols_affected

    # Prueba de telemetría de ejecución estructurada
    result, telemetry = await agent.run_with_telemetry("span_test", SAMPLE_CLEAN_CODE)
    assert isinstance(result, WhiteHatData)
    assert telemetry["hat"] == "white"
    assert telemetry["status"] == "COMPLETED"
    assert telemetry["duration_ms"] >= 0


@pytest.mark.asyncio
async def test_green_hat_agent():
    """Verifica la generación divergente de propuestas del Sombrero Verde."""
    agent = GreenHatAgent()
    proposals = await agent.execute(SAMPLE_CLEAN_CODE, task_context="Optimizar cálculo")
    assert isinstance(proposals, list)
    assert len(proposals) >= 1
    for p in proposals:
        assert isinstance(p, GreenHatProposal)
        assert p.name
        assert p.paradigm
        assert p.tradeoff

    # Prueba de bucle de remediación
    white_data = WhiteHatData(
        symbols_affected=["def test"],
        cyclomatic_complexity=2,
        cognitive_complexity=1,
        maintainability_index=80.0,
        lines_added=5,
        lines_deleted=0,
    )
    critical_finding = BlackHatFinding(
        severity="CRITICAL",
        risk_type="Inyección de Comandos (CWE-78)",
        location="main.py:10",
        description="Falta de sanitización",
        cwe_owasp_id="CWE-78",
    )
    red_assessment = RedHatAssessment(
        cognitive_load_score="Media",
        gut_feeling="Regular",
        ergonomics="Aceptable",
        bloat_score=45.0,
    )
    remediated = await agent.execute_remediation(white_data, [critical_finding], red_assessment)
    assert len(remediated) >= 1
    assert any("Aislamiento" in r.name or "Ponytail" in r.name for r in remediated)


@pytest.mark.asyncio
async def test_black_hat_agent():
    """Verifica la auditoría de seguridad adversarial del Sombrero Negro."""
    agent = BlackHatAgent()
    findings = await agent.execute(SAMPLE_DANGEROUS_CODE)
    assert isinstance(findings, list)
    assert len(findings) >= 3
    severities = {f.severity for f in findings}
    assert "CRITICAL" in severities or "HIGH" in severities
    cwe_ids = {f.cwe_owasp_id for f in findings if f.cwe_owasp_id}
    assert any("CWE" in cid for cid in cwe_ids)


@pytest.mark.asyncio
async def test_yellow_hat_agent():
    """Verifica la identificación de valor y optimizaciones del Sombrero Amarillo."""
    agent = YellowHatAgent()
    benefits = await agent.execute(SAMPLE_CLEAN_CODE)
    assert isinstance(benefits, list)
    assert len(benefits) >= 1
    for b in benefits:
        assert isinstance(b, YellowHatBenefit)
        assert b.metric
        assert b.feasibility in ("ALTA", "MEDIA", "BAJA")


@pytest.mark.asyncio
async def test_red_hat_agent():
    """Verifica la medición psicométrica y el filtro Ponytail del Sombrero Rojo."""
    agent = RedHatAgent()
    assessment = await agent.execute(SAMPLE_OVERENGINEERED_CODE)
    assert isinstance(assessment, RedHatAssessment)
    assert assessment.bloat_score > 0.0
    assert assessment.cognitive_load_score
    assert assessment.gut_feeling
    assert assessment.ergonomics
    assert len(assessment.ladder_violations) > 0


@pytest.mark.asyncio
async def test_blue_hat_agent_consensus():
    """Verifica la consolidación de consenso y emisión de dictamen del Sombrero Azul."""
    blue = BlueHatAgent()
    white = WhiteHatData(
        symbols_affected=["def peligroso"],
        cyclomatic_complexity=3,
        cognitive_complexity=2,
        maintainability_index=45.0,
        lines_added=10,
        lines_deleted=0,
    )
    green = [
        GreenHatProposal(
            name="Arquitectura Segura",
            paradigm="Defensivo",
            description="Aislamiento en sandbox",
            tradeoff="Overhead mínimo",
        )
    ]
    black_clean = [
        BlackHatFinding(
            severity="LOW",
            risk_type="Info",
            location="main.py:1",
            description="Sin riesgo relevante",
        )
    ]
    yellow = [
        YellowHatBenefit(
            metric="Throughput",
            impact="+10 %",
            feasibility="ALTA",
        )
    ]
    red_clean = RedHatAssessment(
        cognitive_load_score="Baja",
        gut_feeling="Limpio",
        ergonomics="Excelente",
        bloat_score=5.0,
    )

    # Caso 1: Código sin riesgos mayores -> APPROVE
    consensus_ok = await blue.execute(
        white=white,
        green=green,
        black=black_clean,
        yellow=yellow,
        red=red_clean,
        original_code=SAMPLE_CLEAN_CODE,
        filepath="clean.py",
    )
    assert isinstance(consensus_ok, SixHatsConsensus)
    assert consensus_ok.verdict == "APPROVE"

    # Caso 2: Código con riesgo crítico -> REQUIRE_CHANGES
    black_critical = [
        BlackHatFinding(
            severity="CRITICAL",
            risk_type="RCE",
            location="main.py:5",
            description="Ejecución remota de código arbitrario",
        )
    ]
    consensus_crit = await blue.execute(
        white=white,
        green=green,
        black=black_critical,
        yellow=yellow,
        red=red_clean,
        original_code=SAMPLE_DANGEROUS_CODE,
        filepath="dangerous.py",
    )
    assert consensus_crit.verdict == "REQUIRE_CHANGES"
    assert any("Mitigado" in m for m in consensus_crit.applied_mitigations)


@pytest.mark.asyncio
async def test_orchestrator_run_agent():
    """Verifica la invocación delegada a través de SixHatsOrchestrator.run_agent."""
    orchestrator = SixHatsOrchestrator()
    w = await orchestrator.run_agent("white", SAMPLE_CLEAN_CODE)
    assert isinstance(w, WhiteHatData)

    k = await orchestrator.run_agent("black", SAMPLE_DANGEROUS_CODE)
    assert isinstance(k, list)
    assert len(k) > 0

    y = await orchestrator.run_agent("yellow", SAMPLE_CLEAN_CODE)
    assert isinstance(y, list)
    assert len(y) > 0

    r = await orchestrator.run_agent("red", SAMPLE_OVERENGINEERED_CODE)
    assert isinstance(r, RedHatAssessment)

    g = await orchestrator.run_agent("green", SAMPLE_CLEAN_CODE)
    assert isinstance(g, list)
    assert len(g) > 0


def test_cli_agent_command(tmp_path):
    """Verifica la ejecución del subcomando CLI six-hats agent en todos los sombreros."""
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(SAMPLE_CLEAN_CODE, encoding="utf-8")

    runner = CliRunner()
    for hat in ["white", "red", "black", "yellow", "green", "blue"]:
        result = runner.invoke(cli, ["agent", hat, str(test_file), "--json"])
        assert result.exit_code == 0, f"Fallo al ejecutar six-hats agent {hat}: {result.output}"
        parsed = json.loads(result.output)
        assert parsed is not None


@pytest.mark.asyncio
async def test_mcp_hat_tools():
    """Verifica la ejecución de las herramientas MCP dedicadas de cada sombrero."""
    w_res = await six_hats_white_hat(SAMPLE_CLEAN_CODE)
    w_json = json.loads(w_res)
    assert "cyclomatic_complexity" in w_json

    g_res = await six_hats_green_hat(SAMPLE_CLEAN_CODE, task_context="Test MCP")
    g_json = json.loads(g_res)
    assert isinstance(g_json, list)
    assert len(g_json) > 0

    k_res = await six_hats_black_hat(SAMPLE_DANGEROUS_CODE)
    k_json = json.loads(k_res)
    assert isinstance(k_json, list)
    assert len(k_json) > 0

    y_res = await six_hats_yellow_hat(SAMPLE_CLEAN_CODE)
    y_json = json.loads(y_res)
    assert isinstance(y_json, list)
    assert len(y_json) > 0

    r_res = await six_hats_red_hat(SAMPLE_OVERENGINEERED_CODE)
    r_json = json.loads(r_res)
    assert "bloat_score" in r_json

    b_res = await six_hats_blue_hat(SAMPLE_CLEAN_CODE, filepath="clean.py")
    b_json = json.loads(b_res)
    assert "consensus" in b_json
