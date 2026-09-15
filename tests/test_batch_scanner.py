import pytest
import json
from pathlib import Path
from click.testing import CliRunner

from six_hats.tools.batch_scanner import (
    discover_source_files,
    run_batch_scan,
    DEFAULT_IGNORED_DIRS,
)
from six_hats.cli import cli
from six_hats.mcp_server import six_hats_batch_scan


def test_discover_source_files(tmp_path):
    """Verifica que el descubrimiento recursivo respete carpetas ignoradas y extensiones."""
    # Archivos válidos
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "modulo_a.py").write_text("def a(): pass\n", encoding="utf-8")
    (src_dir / "modulo_b.py").write_text("def b(): pass\n", encoding="utf-8")

    # Subcarpeta ignorada
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib.py").write_text("def lib(): pass\n", encoding="utf-8")

    # Archivo con extensión no soportada
    (src_dir / "notas.txt").write_text("texto plano\n", encoding="utf-8")

    discovered = discover_source_files(tmp_path)
    discovered_names = [p.name for p in discovered]

    assert "modulo_a.py" in discovered_names
    assert "modulo_b.py" in discovered_names
    assert "lib.py" not in discovered_names
    assert "notas.txt" not in discovered_names


@pytest.mark.asyncio
async def test_run_batch_scan_execution(tmp_path):
    """Verifica la ejecución concurrente del escaneo por lotes y agregación de métricas."""
    file1 = tmp_path / "app1.py"
    file1.write_text("def simple(): return 1\n", encoding="utf-8")

    file2 = tmp_path / "app2.py"
    file2.write_text(
        "import subprocess\ndef riesgo(c): subprocess.run(c, shell=True)\n",
        encoding="utf-8",
    )

    report = await run_batch_scan(tmp_path, concurrency=2)

    assert report.total_files_scanned == 2
    assert report.total_lines_analyzed > 0
    assert report.avg_cyclomatic_complexity >= 1.0
    assert report.critical_vulnerabilities_count >= 1
    assert len(report.hotspots) >= 1
    assert report.hotspots[0]["filepath"] in ("app1.py", "app2.py")


@pytest.mark.asyncio
async def test_run_batch_scan_empty_dir(tmp_path):
    """Verifica el comportamiento seguro ante un directorio sin archivos fuente."""
    empty_dir = tmp_path / "vacio"
    empty_dir.mkdir()

    report = await run_batch_scan(empty_dir)
    assert report.total_files_scanned == 0
    assert report.critical_vulnerabilities_count == 0
    assert len(report.hotspots) == 0


def test_cli_scan_command(tmp_path):
    """Verifica la ejecución del subcomando CLI six-hats scan."""
    sample = tmp_path / "sample.py"
    sample.write_text("def calcular(x): return x * 2\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["scan", str(tmp_path), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["total_files_scanned"] == 1
    assert "avg_cyclomatic_complexity" in data


def test_cli_review_directory_redirection(tmp_path):
    """Verifica que six-hats review redirija a batch scan si se pasa un directorio."""
    sample = tmp_path / "sample2.py"
    sample.write_text("def foo(): return 42\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["review", str(tmp_path), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["total_files_scanned"] == 1


@pytest.mark.asyncio
async def test_mcp_batch_scan_tool(tmp_path):
    """Verifica la ejecución de la herramienta MCP six_hats_batch_scan."""
    sample = tmp_path / "modulo_mcp.py"
    sample.write_text("def saludar(): return 'hola'\n", encoding="utf-8")

    res_str = await six_hats_batch_scan(str(tmp_path))
    data = json.loads(res_str)
    assert data["total_files_scanned"] == 1
    assert "hotspots" in data
