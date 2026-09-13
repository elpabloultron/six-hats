"""Pruebas unitarias para el generador de reportes visuales HTML (html_reporter)."""

import asyncio
from pathlib import Path
from six_hats.core.orchestrator import SixHatsOrchestrator
from six_hats.tools.html_reporter import generate_radar_svg, render_html_report, export_to_html_file

SAMPLE_CODE = """
def calcular_impuesto(monto: float, tasa: float = 0.19) -> float:
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")
    return monto * tasa
"""


def test_generate_radar_svg():
    """Verifica que generate_radar_svg construya las coordenadas y elementos SVG válidos."""
    orchestrator = SixHatsOrchestrator()
    result = asyncio.run(orchestrator.run_full_cycle(SAMPLE_CODE, is_diff=False))

    svg_content = generate_radar_svg(result)
    assert "<svg" in svg_content
    assert "</svg>" in svg_content
    assert "radar-svg" in svg_content
    assert "<polygon" in svg_content
    assert "⚪ Blanco" in svg_content
    assert "🔴 Rojo" in svg_content
    assert "⚫ Negro" in svg_content
    assert "🟡 Amarillo" in svg_content
    assert "🟢 Verde" in svg_content
    assert "🔵 Azul" in svg_content


def test_render_html_report_zero_cdns():
    """Verifica que el reporte HTML sea autocontenido y no contenga enlaces a CDNs externas."""
    orchestrator = SixHatsOrchestrator()
    result = asyncio.run(orchestrator.run_full_cycle(SAMPLE_CODE, is_diff=False))

    html_content = render_html_report(result, filepath="impuestos.py")
    assert "<!DOCTYPE html>" in html_content
    assert "<title>Reporte de Revisión de Seis Sombreros — impuestos.py</title>" in html_content
    assert "radar-svg" in html_content
    assert "Sombrero Negro" in html_content
    assert "Sombrero Verde" in html_content
    assert "Sombrero Amarillo" in html_content
    assert "Sombrero Rojo" in html_content
    assert "Sombrero Blanco" in html_content
    assert "Dictamen del Sombrero Azul" in html_content

    # Cero CDNs externas o scripts remotos (Principio Ponytail)
    assert "<script src=" not in html_content
    assert "cdn." not in html_content
    assert "https://cdnjs" not in html_content
    assert "https://unpkg" not in html_content
    assert "https://jsdelivr" not in html_content


def test_export_to_html_file(tmp_path: Path):
    """Verifica que export_to_html_file escriba el archivo en el sistema de archivos."""
    orchestrator = SixHatsOrchestrator()
    result = asyncio.run(orchestrator.run_full_cycle(SAMPLE_CODE, is_diff=False))

    target_file = tmp_path / "subfolder" / "dashboard.html"
    export_to_html_file(result, str(target_file), filepath="impuestos.py")

    assert target_file.exists()
    content = target_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "impuestos.py" in content
