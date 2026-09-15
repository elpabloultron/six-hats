import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from six_hats.cli import cli

SAMPLE_CODE = """
def calcular(a, b):
    \"\"\"Calculo simple sin riesgos.\"\"\"
    return a + b
"""

SAMPLE_RISKY_CODE = """
import os
def peligro(cmd):
    eval(cmd)
"""


def test_cli_debate_command():
    """Verifica el subcomando debate entre Sombrero Negro y Verde."""
    runner = CliRunner()
    result = runner.invoke(cli, ["debate", "Arquitectura orientada a eventos con Kafka"])
    assert result.exit_code == 0
    assert "Debatiendo propuesta arquitectónica" in result.output
    assert "Sombrero Negro" in result.output
    assert "Sombrero Verde" in result.output
    assert "Sombrero Azul" in result.output


def test_cli_ponytail_command(tmp_path):
    """Verifica el subcomando ponytail con salida de terminal y JSON."""
    code_file = tmp_path / "ponytail_sample.py"
    code_file.write_text(SAMPLE_CODE, encoding="utf-8")

    runner = CliRunner()
    res_text = runner.invoke(cli, ["ponytail", str(code_file)])
    assert res_text.exit_code == 0
    assert "Auditoría Ponytail" in res_text.output

    res_json = runner.invoke(cli, ["ponytail", str(code_file), "--json"])
    assert res_json.exit_code == 0
    parsed = json.loads(res_json.output)
    assert "bloat_score" in parsed


def test_cli_review_sarif_and_html(tmp_path):
    """Verifica exportación de SARIF y HTML desde el subcomando review."""
    code_file = tmp_path / "app.py"
    code_file.write_text(SAMPLE_CODE, encoding="utf-8")
    sarif_out = tmp_path / "report.sarif"
    html_out = tmp_path / "report.html"

    runner = CliRunner()
    res = runner.invoke(
        cli,
        ["review", str(code_file), "--sarif", str(sarif_out), "--html", str(html_out)],
    )
    assert res.exit_code == 0
    assert sarif_out.exists()
    assert html_out.exists()


def test_cli_review_fail_on_critical(tmp_path):
    """Verifica que --fail-on CRITICAL termine con código 1 ante vulnerabilidad crítica."""
    bad_file = tmp_path / "vulnerable.py"
    bad_file.write_text(SAMPLE_RISKY_CODE, encoding="utf-8")

    runner = CliRunner()
    res = runner.invoke(cli, ["review", str(bad_file), "--fail-on", "CRITICAL"])
    assert res.exit_code == 1
    assert "FALLO EN CONTROL DE CALIDAD" in res.output


def test_cli_agent_fail_on(tmp_path):
    """Verifica que el subcomando agent respete --fail-on."""
    bad_file = tmp_path / "vulnerable_agent.py"
    bad_file.write_text(SAMPLE_RISKY_CODE, encoding="utf-8")

    runner = CliRunner()
    res = runner.invoke(cli, ["agent", "black", str(bad_file), "--fail-on", "CRITICAL"])
    assert res.exit_code == 1
    assert "FALLO EN CONTROL DE CALIDAD" in res.output


def test_cli_plugin_install_dry_run():
    """Verifica el subcomando plugin install en modo simulación dry-run."""
    runner = CliRunner()
    res = runner.invoke(cli, ["plugin", "install", "claude", "--dry-run"])
    assert res.exit_code == 0
    assert "Instalando six-hats como plugin" in res.output


def test_cli_export_tools_formats():
    """Verifica la exportación de herramientas en formato hermes-chatml y openai."""
    runner = CliRunner()
    res_hermes = runner.invoke(cli, ["export-tools", "--format", "hermes-chatml"])
    assert res_hermes.exit_code == 0
    assert "<tools>" in res_hermes.output

    res_openai = runner.invoke(cli, ["export-tools", "--format", "openai"])
    assert res_openai.exit_code == 0
    parsed = json.loads(res_openai.output)
    assert isinstance(parsed, list)
