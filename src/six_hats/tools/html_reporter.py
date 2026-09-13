"""Generador de reportes visuales autónomos en HTML5 para Six Hats.

Genera un dashboard interactivo, moderno y autocontenido con gráficos de radar
en SVG puro, métricas AST, desglose de sombreros e invariantes de prueba,
respetando el principio Ponytail (cero dependencias de CDNs externas).
"""

from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any, Dict, List

from six_hats.core.models import SixHatsReviewResult


def _calculate_radar_points(
    values: list[float],
    center_x: float = 200.0,
    center_y: float = 200.0,
    radius: float = 140.0,
) -> tuple[str, list[tuple[float, float]]]:
    """Calcula las coordenadas de los vértices de un polígono de radar de 6 ejes."""
    points: list[tuple[float, float]] = []
    # 6 ejes espaciados a 60 grados (pi / 3 radianes), iniciando a las 12 en punto (-pi / 2)
    start_angle = -math.pi / 2.0
    for i, val in enumerate(values):
        val_clamped = max(5.0, min(100.0, float(val)))
        r = (val_clamped / 100.0) * radius
        angle = start_angle + (i * 2.0 * math.pi / 6.0)
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        points.append((round(x, 1), round(y, 1)))

    svg_points = " ".join([f"{x},{y}" for x, y in points])
    return svg_points, points


def generate_radar_svg(result: SixHatsReviewResult) -> str:
    """Genera el código SVG vectorial autónomo del gráfico de radar de los 6 Sombreros."""
    # Valores de los 6 sombreros en escala 0-100:
    # 1. Blanco: Maintainability Index
    val_white = max(10.0, min(100.0, result.white.maintainability_index))

    # 2. Rojo: Ergonomía DX (inverso de bloat score y carga cognitiva)
    val_red = max(10.0, min(100.0, 100.0 - (result.red.bloat_score * 0.7 + result.red.visual_clutter_score * 0.3)))

    # 3. Negro: Robustez / Ausencia de vulnerabilidades críticas
    critical_or_high = len([f for f in result.black if f.severity in ("CRITICAL", "HIGH")])
    val_black = max(10.0, min(100.0, 100.0 - (critical_or_high * 25.0 + len(result.black) * 5.0)))

    # 4. Amarillo: Valor proyectado y optimización
    val_yellow = max(20.0, min(100.0, 40.0 + len(result.yellow) * 20.0))

    # 5. Verde: Potencial de innovación arquitectónica
    val_green = max(20.0, min(100.0, 35.0 + len(result.green) * 20.0))

    # 6. Azul: Solidez de consenso
    if result.consensus.verdict == "APPROVE":
        val_blue = 95.0
    elif result.consensus.verdict == "CONDITIONAL":
        val_blue = 65.0
    else:
        val_blue = 30.0

    hat_values = [val_white, val_red, val_black, val_yellow, val_green, val_blue]
    hat_labels = [
        ("⚪ Blanco", "Telemetría"),
        ("🔴 Rojo", "Ergonomía"),
        ("⚫ Negro", "Seguridad"),
        ("🟡 Amarillo", "Valor"),
        ("🟢 Verde", "Innovación"),
        ("🔵 Azul", "Síntesis"),
    ]

    cx, cy, r_max = 200.0, 200.0, 140.0
    svg_points, coords = _calculate_radar_points(hat_values, cx, cy, r_max)

    # Coordenadas de los ejes radiales al 100%
    axis_lines = []
    labels_svg = []
    start_angle = -math.pi / 2.0

    for i, (name, sub) in enumerate(hat_labels):
        angle = start_angle + (i * 2.0 * math.pi / 6.0)
        ex = cx + r_max * math.cos(angle)
        ey = cy + r_max * math.sin(angle)
        axis_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#30363d" stroke-width="1.5" stroke-dasharray="3,3" />')

        # Posición de la etiqueta con margen exterior
        lx = cx + (r_max + 28.0) * math.cos(angle)
        ly = cy + (r_max + 20.0) * math.sin(angle)
        text_anchor = "middle"
        if math.cos(angle) > 0.3:
            text_anchor = "start"
        elif math.cos(angle) < -0.3:
            text_anchor = "end"

        labels_svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{text_anchor}" fill="#f0f6fc" font-size="12" font-weight="bold">'
            f'{name}'
            f'<tspan x="{lx:.1f}" dy="14" fill="#8b949e" font-size="10" font-weight="normal">{sub} ({round(hat_values[i])}%)</tspan>'
            f'</text>'
        )

    # Círculos concéntricos de referencia (25%, 50%, 75%, 100%)
    grids = []
    for pct in [0.25, 0.50, 0.75, 1.0]:
        grid_r = r_max * pct
        _, grid_points = _calculate_radar_points([pct * 100.0] * 6, cx, cy, r_max)
        poly_str = " ".join([f"{x},{y}" for x, y in grid_points])
        grids.append(f'<polygon points="{poly_str}" fill="none" stroke="#21262d" stroke-width="1" />')

    # Marcadores en los vértices del radar
    dots_svg = []
    for (x, y), val, (name, _) in zip(coords, hat_values, hat_labels):
        dots_svg.append(
            f'<circle cx="{x}" cy="{y}" r="5" fill="#58a6ff" stroke="#0d1117" stroke-width="2">'
            f'<title>{name}: {round(val)}%</title>'
            f'</circle>'
        )

    return f"""
    <svg viewBox="0 0 400 400" width="100%" height="340" xmlns="http://www.w3.org/2000/svg" class="radar-svg">
        <g class="radar-grid">
            {''.join(grids)}
            {''.join(axis_lines)}
        </g>
        <polygon points="{svg_points}" fill="rgba(56, 139, 253, 0.25)" stroke="#58a6ff" stroke-width="2.5" />
        <g class="radar-dots">
            {''.join(dots_svg)}
        </g>
        <g class="radar-labels">
            {''.join(labels_svg)}
        </g>
    </svg>
    """


def render_html_report(
    result: SixHatsReviewResult,
    filepath: str = "código",
    graph_data: Dict[str, Any] | None = None,
) -> str:
    """Renderiza el documento HTML5 completo con todos los datos de la revisión."""
    radar_svg = generate_radar_svg(result)

    # Colores semánticos del veredicto
    verdict = result.consensus.verdict
    if verdict == "APPROVE":
        verdict_badge_class = "badge-approve"
        verdict_text = "✓ APROBADO (APPROVE)"
    elif verdict == "CONDITIONAL":
        verdict_badge_class = "badge-conditional"
        verdict_text = "⚠ APROBADO CON CONDICIONES"
    else:
        verdict_badge_class = "badge-reject"
        verdict_text = "✖ RECHAZADO (REJECT)"

    # Formateo de hallazgos del Sombrero Negro
    black_rows = []
    for finding in result.black:
        sev = finding.severity.upper()
        sev_class = f"sev-{sev.lower()}"
        black_rows.append(f"""
        <tr class="finding-row">
            <td><span class="badge {sev_class}">{html.escape(sev)}</span></td>
            <td><strong>{html.escape(finding.risk_type)}</strong><br><small>{html.escape(finding.cwe_owasp_id or '')}</small></td>
            <td><code>{html.escape(finding.location)}</code></td>
            <td>{html.escape(finding.description)}</td>
        </tr>
        """)
    black_table_content = "".join(black_rows) if black_rows else '<tr><td colspan="4">No se detectaron hallazgos de severidad.</td></tr>'

    # Invariantes de prueba (Hypothesis)
    sample_invariants = result.black[0].property_invariants if result.black else []
    invariants_list = "".join([f"<li><code>{html.escape(inv)}</code></li>" for inv in sample_invariants]) or "<li>Invariantes estándar de no-regresión.</li>"

    # Propuestas del Sombrero Verde
    green_cards = []
    for prop in result.green:
        green_cards.append(f"""
        <div class="card card-green">
            <div class="card-header">
                <strong>{html.escape(prop.name)}</strong>
                <span class="badge badge-paradigm">{html.escape(prop.paradigm)}</span>
            </div>
            <p>{html.escape(prop.description)}</p>
            <div class="tradeoff-box">
                <small><strong>Trade-off / Compensación:</strong> {html.escape(prop.tradeoff)}</small>
            </div>
        </div>
        """)
    green_content = "".join(green_cards)

    # Beneficios del Sombrero Amarillo
    yellow_rows = []
    for ben in result.yellow:
        yellow_rows.append(f"""
        <tr>
            <td><strong>{html.escape(ben.metric)}</strong></td>
            <td>{html.escape(ben.impact)}</td>
            <td><span class="badge badge-feasibility">{html.escape(ben.feasibility)}</span></td>
        </tr>
        """)
    yellow_table_content = "".join(yellow_rows)

    # Violaciones Ponytail
    ponytail_violations = "".join([f"<li>{html.escape(v)}</li>" for v in result.red.ladder_violations]) or "<li>Ninguna violación detectada. Código sobrio y sin sobreingeniería.</li>"
    lexical_warnings = "".join([f"<li>{html.escape(w)}</li>" for w in result.red.lexical_confusion_warnings]) or "<li>Nombres de variables claros y sin similitud confusa.</li>"

    # Mitigaciones aplicadas Sombrero Azul
    mitigations_items = "".join([f"<li>{html.escape(m)}</li>" for m in result.consensus.applied_mitigations]) or "<li>Sin acciones de remediación pendientes.</li>"

    # Parche de código si existe
    patch_block = ""
    if result.consensus.code_patch:
        patch_escaped = html.escape(result.consensus.code_patch)
        patch_block = f"""
        <div class="card section-card">
            <h3>🩹 Parche de Remediación Generado (Unified Diff)</h3>
            <pre class="diff-block"><code>{patch_escaped}</code></pre>
        </div>
        """

    # Bloque de información de grafo (si fue provisto por Graphify o AST)
    graph_section = ""
    if graph_data:
        god_nodes = graph_data.get("god_nodes", [])
        communities = graph_data.get("communities", [])
        source_engine = graph_data.get("source", "AST Nativo")
        god_nodes_html = "".join([f"<li><code>{html.escape(node)}</code></li>" for node in god_nodes]) or "<li>No se detectaron nodos con centralidad excesiva.</li>"
        graph_section = f"""
        <div class="card section-card">
            <h3>🕸️ Análisis Estructural de Dependencias y Grafo ({html.escape(source_engine)})</h3>
            <div class="graph-grid">
                <div>
                    <h4>God Nodes / Componentes Críticos</h4>
                    <ul class="clean-list">{god_nodes_html}</ul>
                </div>
                <div>
                    <h4>Comunidades y Módulos</h4>
                    <p>Total de clusters identificados: <strong>{len(communities)}</strong></p>
                </div>
            </div>
        </div>
        """

    # Ensamblado del HTML5 autocontenido
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Revisión de Seis Sombreros — {html.escape(filepath)}</title>
    <style>
        :root {{
            --bg-color: #0d1117;
            --surface-color: #161b22;
            --border-color: #30363d;
            --text-main: #c9d1d9;
            --text-heading: #f0f6fc;
            --text-muted: #8b949e;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-red: #f85149;
            --accent-yellow: #d29922;
            --accent-purple: #bc8cff;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: var(--font-family);
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1, h2, h3, h4 {{ color: var(--text-heading); font-weight: 600; }}
        header h1 {{ font-size: 1.6rem; display: flex; align-items: center; gap: 10px; }}
        header p {{ color: var(--text-muted); font-size: 0.9rem; margin-top: 4px; }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-approve {{ background-color: rgba(63, 185, 80, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-conditional {{ background-color: rgba(210, 153, 34, 0.2); color: var(--accent-yellow); border: 1px solid var(--accent-yellow); }}
        .badge-reject {{ background-color: rgba(248, 81, 73, 0.2); color: var(--accent-red); border: 1px solid var(--accent-red); }}
        .badge-paradigm {{ background-color: #21262d; color: var(--accent-blue); }}
        .badge-feasibility {{ background-color: #21262d; color: var(--accent-green); }}

        .sev-critical {{ background-color: #f85149; color: #ffffff; }}
        .sev-high {{ background-color: rgba(248, 81, 73, 0.3); color: #ff7b72; border: 1px solid #f85149; }}
        .sev-medium {{ background-color: rgba(210, 153, 34, 0.3); color: #e3b341; border: 1px solid #d29922; }}
        .sev-low {{ background-color: #21262d; color: var(--text-muted); border: 1px solid var(--border-color); }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        @media (max-width: 900px) {{
            .dashboard-grid {{ grid-template-columns: 1fr; }}
        }}

        .card {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .radar-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            margin-top: 16px;
            width: 100%;
        }}
        .kpi-box {{
            background-color: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }}
        .kpi-val {{ font-size: 1.4rem; font-weight: bold; color: var(--text-heading); }}
        .kpi-lbl {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; margin-top: 4px; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            margin-top: 10px;
        }}
        th, td {{
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{ color: var(--text-muted); font-weight: 600; background-color: #12161c; }}

        code {{
            background-color: rgba(110, 118, 129, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
            font-size: 0.85em;
        }}
        pre.diff-block {{
            background-color: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            color: #79c0ff;
            font-size: 0.85rem;
            margin-top: 12px;
        }}

        ul.clean-list {{
            list-style: none;
            padding-left: 0;
            margin-top: 8px;
        }}
        ul.clean-list li {{
            padding: 6px 0;
            border-bottom: 1px solid #21262d;
            font-size: 0.88rem;
        }}
        .tradeoff-box {{
            background-color: #0d1117;
            padding: 8px 12px;
            border-left: 3px solid var(--accent-yellow);
            border-radius: 4px;
            margin-top: 10px;
        }}
        .footer-note {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🎩 Six Hats Executive Report</h1>
                <p>Archivo auditado: <code>{html.escape(filepath)}</code> · Metodología Edward de Bono</p>
            </div>
            <div>
                <span class="badge {verdict_badge_class}">{verdict_text}</span>
            </div>
        </header>

        <div class="dashboard-grid">
            <div class="card radar-card">
                <h3>Balance Cognitivo de los 6 Sombreros</h3>
                {radar_svg}
            </div>

            <div class="card">
                <h3>Dictamen del Sombrero Azul</h3>
                <p style="margin-top: 10px; font-size: 0.95rem;">{html.escape(result.consensus.summary)}</p>

                <div class="kpi-grid">
                    <div class="kpi-box">
                        <div class="kpi-val">{result.white.cyclomatic_complexity}</div>
                        <div class="kpi-lbl">Ciclomática</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val">{result.white.cognitive_complexity}</div>
                        <div class="kpi-lbl">Cognitiva</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val">{result.white.maintainability_index}</div>
                        <div class="kpi-lbl">Mantenibilidad</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-val">{result.red.bloat_score} %</div>
                        <div class="kpi-lbl">Bloat Ponytail</div>
                    </div>
                </div>

                <div style="margin-top: 18px;">
                    <h4>Mitigaciones Acordadas:</h4>
                    <ul class="clean-list">
                        {mitigations_items}
                    </ul>
                </div>
            </div>
        </div>

        {graph_section}

        <div class="card section-card">
            <h3>⚫ Sombrero Negro: Riesgos Críticos, OWASP e Invariantes</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 100px;">Severidad</th>
                        <th>Riesgo / CWE</th>
                        <th>Ubicación</th>
                        <th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    {black_table_content}
                </tbody>
            </table>

            <h4 style="margin-top: 20px;">🧪 Invariantes de Fuzzing por Propiedades (Hypothesis):</h4>
            <ul class="clean-list">
                {invariants_list}
            </ul>
        </div>

        <div class="card section-card">
            <h3>🟢 Sombrero Verde: Alternativas de Arquitectura e Innovación</h3>
            {green_content}
        </div>

        <div class="card section-card">
            <h3>🟡 Sombrero Amarillo: Rendimiento, Optimización y Factibilidad</h3>
            <table>
                <thead>
                    <tr>
                        <th>Métrica de Optimización</th>
                        <th>Impacto Proyectado</th>
                        <th>Factibilidad</th>
                    </tr>
                </thead>
                <tbody>
                    {yellow_table_content}
                </tbody>
            </table>
        </div>

        <div class="card section-card">
            <h3>🔴 Sombrero Rojo: Experiencia de Desarrollo y Auditoría Ponytail</h3>
            <p><strong>Sensación Visceral (Gut Feeling):</strong> {html.escape(result.red.gut_feeling)}</p>
            <p><strong>Ergonomía a las 3:00 AM:</strong> {html.escape(result.red.ergonomics)}</p>
            <p><strong>Veredicto Anti-Sobreingeniería Ponytail:</strong> <code>{html.escape(result.red.ponytail_verdict)}</code> (~{result.red.lines_reducible_pct} % líneas reducibles)</p>

            <h4 style="margin-top: 14px;">Violaciones a la Escalera de la Pereza:</h4>
            <ul class="clean-list">
                {ponytail_violations}
            </ul>

            <h4 style="margin-top: 14px;">Advertencias de Confusión Léxica de Variables:</h4>
            <ul class="clean-list">
                {lexical_warnings}
            </ul>
        </div>

        <div class="card section-card">
            <h3>⚪ Sombrero Blanco: Telemetría y Hechos Fácticos</h3>
            <p><strong>Líneas Añadidas / Eliminadas:</strong> +{result.white.lines_added} / -{result.white.lines_deleted}</p>
            <p><strong>Símbolos Detectados:</strong> <code>{html.escape(", ".join(result.white.symbols_affected) or "Ninguno")}</code></p>
            <p><strong>Dependencias Importadas:</strong> <code>{html.escape(", ".join(result.white.dependencies) or "Ninguna")}</code></p>
            {f'<p><strong>Volatilidad Git (Churn Score):</strong> {result.white.git_churn_score} ({result.white.historical_risk})</p>' if result.white.git_churn_score else ''}
            {f'<p><strong>Cobertura de Tests:</strong> {html.escape(result.white.coverage_summary)}</p>' if result.white.coverage_summary else ''}
        </div>

        {patch_block}

        <div class="footer-note">
            Generado por <strong>six-hats v0.1.0</strong> · Filosofía Ponytail: Cero dependencias externas pesadas · Todos los derechos reservados.
        </div>
    </div>
</body>
</html>
"""


def export_to_html_file(
    result: SixHatsReviewResult,
    output_path: str,
    filepath: str = "código",
    graph_data: Dict[str, Any] | None = None,
) -> None:
    """Guarda el reporte renderizado en la ruta de archivo especificada."""
    html_content = render_html_report(result, filepath=filepath, graph_data=graph_data)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")
