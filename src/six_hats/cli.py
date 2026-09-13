import click
import asyncio
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from six_hats.core.orchestrator import SixHatsOrchestrator
from six_hats.tools.git_utils import get_git_diff
from six_hats.tools.ponytail_rules import audit_ponytail
from six_hats.tools.sarif_exporter import export_to_sarif_file
from six_hats.tools.exporter import export_tools_by_format
from six_hats.tools.plugin_installer import install_plugin
from six_hats.tools.html_reporter import export_to_html_file
from six_hats.tools.graph_analyzer import detect_codebase_graph

console = Console()


@click.group()
def cli():
    """CLI de razonamiento paralelo de Seis Sombreros para ingeniería de software."""
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True), required=False)
@click.option("--git-diff", "-g", is_flag=True, help="Usa el git diff del repositorio actual como entrada.")
@click.option("--context", "-c", default="", help="Contexto adicional del requerimiento o problema.")
@click.option("--json-output", "--json", "json_mode", is_flag=True, help="Emite salida estructurada pura en JSON para CI/CD.")
@click.option("--sarif", type=click.Path(), default=None, help="Ruta de destino para exportar informe SARIF v2.1.0.")
@click.option("--html-report", "--html", "html_path", type=click.Path(), default=None, help="Ruta de destino para exportar informe visual HTML interactivo.")
@click.option("--with-graph", is_flag=True, help="Enriquece el análisis con la topología de grafo (Graphify o subgrafo AST).")
@click.option("--fail-on", type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "BLOAT"], case_sensitive=False), default=None, help="Falla con código 1 ante hallazgos de severidad especificada.")
def review(
    filepath: str | None,
    git_diff: bool,
    context: str,
    json_mode: bool,
    sarif: str | None,
    html_path: str | None,
    with_graph: bool,
    fail_on: str | None,
):
    """Ejecuta una revisión completa multifacética de 6 Sombreros sobre un archivo o git diff."""
    if git_diff:
        code_content = get_git_diff(filepath)
        if not code_content.strip():
            if not json_mode:
                console.print("[yellow]No se detectaron cambios en el git diff actual.[/yellow]")
            else:
                click.echo(json.dumps({"status": "no_diff"}))
            return
        is_diff = True
        target_name = filepath or "git_diff.patch"
    elif filepath:
        target_path = Path(filepath)
        code_content = target_path.read_text(encoding="utf-8", errors="replace")
        is_diff = target_path.suffix in [".diff", ".patch"]
        target_name = filepath
    else:
        if not json_mode:
            console.print("[red]Error: Debe especificar un archivo o usar la opción --git-diff.[/red]")
        sys.exit(1)

    if not json_mode:
        console.print(Panel.fit("[bold blue]Iniciando orquestación de 6 Sombreros (Edward de Bono)...[/bold blue]"))

    orchestrator = SixHatsOrchestrator()
    result = asyncio.run(
        orchestrator.run_full_cycle(
            code_content, is_diff=is_diff, task_context=context, filepath=target_name
        )
    )

    # 1. Análisis de grafo si se requiere
    graph_data = None
    if html_path or with_graph:
        graph_data = detect_codebase_graph(code_content=code_content)

    # 2. Exportación SARIF si se solicitó
    if sarif:
        export_to_sarif_file(result, sarif, filepath=target_name)
        if not json_mode:
            console.print(f"[green]✓ Informe SARIF v2.1.0 exportado exitosamente a:[/green] {sarif}")

    # 3. Exportación HTML si se solicitó
    if html_path:
        export_to_html_file(result, html_path, filepath=target_name, graph_data=graph_data)
        if not json_mode:
            console.print(f"[green]✓ Dashboard visual HTML exportado exitosamente a:[/green] {html_path}")

    # 4. Salida JSON pura para pipelines
    if json_mode:
        click.echo(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    else:
        # Renderizado interactivo Rich en terminal
        # Sombrero Blanco
        white_table = Table(title="⚪ Sombrero Blanco: Telemetría, Hechos y Métricas Estáticas", border_style="white")
        white_table.add_column("Métrica / Indicador", style="bold")
        white_table.add_column("Valor Calculado")
        white_table.add_row("Archivo / Objetivo", target_name)
        white_table.add_row("Complejidad Ciclomática (McCabe)", str(result.white.cyclomatic_complexity))
        white_table.add_row("Complejidad Cognitiva (SonarSource)", str(result.white.cognitive_complexity))
        white_table.add_row("Índice de Mantenibilidad (SEI/Radon)", f"{result.white.maintainability_index} / 100")
        white_table.add_row("Líneas Añadidas / Eliminadas", f"+{result.white.lines_added} / -{result.white.lines_deleted}")
        if result.white.git_churn_score:
            churn_style = "bold red" if result.white.historical_risk == "HIGH_HOTSPOT" else "yellow"
            white_table.add_row("Volatilidad Histórica Git (pydriller)", f"[{churn_style}]{result.white.git_churn_score}[/{churn_style}]")
        if result.white.coverage_summary:
            white_table.add_row("Cobertura Real de Tests", result.white.coverage_summary)
        white_table.add_row("Símbolos Detectados", ", ".join(result.white.symbols_affected[:6]) or "Ninguno")
        white_table.add_row("Dependencias / Imports", ", ".join(result.white.dependencies) or "Ninguna")
        console.print(white_table)

        # Sombrero Verde
        green_table = Table(title="🟢 Sombrero Verde: Alternativas Arquitectónicas (GoF / Returns)", border_style="green")
        green_table.add_column("Propuesta", style="bold green")
        green_table.add_column("Paradigma", style="cyan")
        green_table.add_column("Descripción")
        green_table.add_column("Trade-off", style="italic")
        for prop in result.green:
            green_table.add_row(prop.name, prop.paradigm, prop.description, prop.tradeoff)
        console.print(green_table)

        # Sombrero Negro
        black_table = Table(title="⚫ Sombrero Negro: Juicio Crítico y Seguridad (Semgrep / Bandit / OWASP)", border_style="red")
        black_table.add_column("Severidad", style="bold")
        black_table.add_column("Tipo de Riesgo / CWE", style="bold red")
        black_table.add_column("Ubicación")
        black_table.add_column("Descripción")
        for finding in result.black:
            sev_color = "red" if finding.severity in ("CRITICAL", "HIGH") else "yellow"
            black_table.add_row(
                f"[{sev_color}]{finding.severity}[/{sev_color}]",
                finding.risk_type,
                finding.location,
                finding.description,
            )
        console.print(black_table)

        # Invariantes de Propiedad (Hypothesis)
        sample_invariants = result.black[0].property_invariants if result.black else []
        if sample_invariants:
            inv_txt = "\n".join([f"• {inv}" for inv in sample_invariants])
            console.print(Panel(inv_txt, title="🧪 Invariantes de Prueba por Propiedades (Hypothesis Fuzzing)", border_style="red"))

        # Sombrero Amarillo
        yellow_table = Table(title="🟡 Sombrero Amarillo: Valor, Eficiencia y Beneficios (Ruff / Big-O)", border_style="yellow")
        yellow_table.add_column("Métrica", style="bold yellow")
        yellow_table.add_column("Impacto Proyectado")
        yellow_table.add_column("Factibilidad", style="green")
        for ben in result.yellow:
            yellow_table.add_row(ben.metric, ben.impact, ben.feasibility)
        console.print(yellow_table)

        # Sombrero Rojo
        ponytail_color = "green" if result.red.bloat_score <= 20 else ("yellow" if result.red.bloat_score <= 40 else "red")
        ponytail_violations_txt = "\n".join([f"  • {v}" for v in result.red.ladder_violations]) or "  • Ninguna violación detectada."
        confusion_txt = "\n".join([f"  • {w}" for w in result.red.lexical_confusion_warnings]) or "  • Ninguna colisión léxica identificada."
        red_content = (
            f"[bold]Carga Cognitiva:[/bold] {result.red.cognitive_load_score}\n"
            f"[bold]Sensación Visceral (Gut Feeling):[/bold] {result.red.gut_feeling}\n"
            f"[bold]Ergonomía a las 3:00 AM:[/bold] {result.red.ergonomics}\n"
            f"[bold]Saturación y Ruido Visual:[/bold] {result.red.visual_clutter_score} %\n\n"
            f"[bold]Confusión Léxica de Variables (RapidFuzz):[/bold]\n{confusion_txt}\n\n"
            f"[bold]Filtro Ponytail Anti-Sobreingeniería:[/bold] [{ponytail_color}]{result.red.ponytail_verdict}[/{ponytail_color}]\n"
            f"[bold]Líneas Reducibles Estimadas:[/bold] ~{result.red.lines_reducible_pct} %\n"
            f"[bold]Violaciones a la Escalera de la Pereza:[/bold]\n{ponytail_violations_txt}"
        )
        console.print(Panel(red_content, title="🔴 Sombrero Rojo: DX, Ergonomía y Filtro Ponytail", border_style="magenta"))

        # Sombrero Azul
        verdict_style = "green" if result.consensus.verdict == "APPROVE" else "bold red"
        mitigations_txt = "\n".join([f"• {m}" for m in result.consensus.applied_mitigations])
        veto_status = "[bold red]VETO APLICADO (Exceso de Abstracciones)[/bold red]" if result.consensus.ponytail_veto_applied else "[green]Alineado con Principio YAGNI[/green]"
        loopback_status = f"[bold yellow]{result.feedback_loop_count} ciclo(s) de remediación ejecutados[/bold yellow]" if result.feedback_loop_count > 0 else "[green]Aprobado en primera iteración directa[/green]"
        blue_content = (
            f"[bold]Veredicto:[/bold] [{verdict_style}]{result.consensus.verdict}[/{verdict_style}]\n"
            f"[bold]Arquitectura Seleccionada:[/bold] {result.consensus.selected_architecture}\n"
            f"[bold]Bucle Dialéctico Cíclico (LangGraph):[/bold] {loopback_status}\n"
            f"[bold]Veto de Simplicidad Ponytail:[/bold] {veto_status}\n\n"
            f"[bold]Síntesis Ejecutiva:[/bold]\n{result.consensus.summary}\n\n"
            f"[bold]Mitigaciones Aplicadas:[/bold]\n{mitigations_txt}"
        )
        console.print(Panel(blue_content, title="🔵 Sombrero Azul: Síntesis y Dictamen Final", border_style="cyan"))

        # Trazabilidad OpenTelemetry Spans
        if result.deliberation_trace:
            trace_table = Table(title="📡 Telemetría de Deliberación (Trazas OpenTelemetry Spans)", border_style="cyan")
            trace_table.add_column("Span", style="bold cyan")
            trace_table.add_column("Sombrero")
            trace_table.add_column("Duración", style="yellow")
            trace_table.add_column("Resumen")
            for sp in result.deliberation_trace:
                trace_table.add_row(sp.get("span_name", ""), sp.get("hat", ""), f"{sp.get('duration_ms', 0)} ms", sp.get("summary", ""))
            console.print(trace_table)

        if result.consensus.code_patch:
            console.print("\n[bold cyan]Parche de Mitigación Generado (Unified Diff Real):[/bold cyan]")
            syntax = Syntax(result.consensus.code_patch, "diff", theme="monokai", line_numbers=False)
            console.print(syntax)

    # 3. Evaluación de salida ante flag --fail-on en CI/CD
    if fail_on:
        fail_on_upper = fail_on.upper()
        severities = {f.severity for f in result.black}
        failed = False
        reason = ""

        if fail_on_upper == "CRITICAL" and "CRITICAL" in severities:
            failed, reason = True, "Se detectaron hallazgos de severidad CRITICAL."
        elif fail_on_upper == "HIGH" and severities.intersection({"CRITICAL", "HIGH"}):
            failed, reason = True, "Se detectaron hallazgos de severidad HIGH o CRITICAL."
        elif fail_on_upper == "MEDIUM" and severities.intersection({"CRITICAL", "HIGH", "MEDIUM"}):
            failed, reason = True, "Se detectaron hallazgos de severidad MEDIUM, HIGH o CRITICAL."
        elif fail_on_upper == "BLOAT" and result.red.bloat_score > 25.0:
            failed, reason = True, f"Índice de sobreingeniería Ponytail ({result.red.bloat_score} %) superó el 25 %."

        if failed:
            if not json_mode:
                console.print(f"\n[bold red]✖ FALLO EN CONTROL DE CALIDAD CI/CD (--fail-on {fail_on}):[/bold red] {reason}")
            sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--threshold", "-t", default=25.0, help="Umbral máximo admisible de sobreingeniería (%).")
@click.option("--json-output", "--json", "json_mode", is_flag=True, help="Emite el reporte en formato JSON puro.")
@click.option("--fail-on-bloat", is_flag=True, help="Termina con código 1 si el bloat score supera el umbral.")
def ponytail(filepath: str, threshold: float, json_mode: bool, fail_on_bloat: bool):
    """Ejecuta una auditoría estricta contra la Escalera de la Pereza de Ponytail para eliminar sobreingeniería."""
    target_path = Path(filepath)
    code_content = target_path.read_text(encoding="utf-8", errors="replace")

    report = audit_ponytail(code_content, max_acceptable_bloat=threshold)

    if json_mode:
        click.echo(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
    else:
        console.print(Panel.fit(f"[bold magenta]Auditoría Ponytail (Escalera de la Pereza):[/bold magenta] {filepath}"))

        score_color = "green" if report.bloat_score <= 20 else ("yellow" if report.bloat_score <= 40 else "red")
        summary_panel = (
            f"[bold]Líneas analizadas:[/bold] {report.lines_analyzed}\n"
            f"[bold]Índice de Sobreingeniería (Bloat Score):[/bold] [{score_color}]{report.bloat_score} %[/{score_color}]\n"
            f"[bold]Líneas prescindibles estimadas:[/bold] {report.estimated_lines_reducible} "
            f"({round((report.estimated_lines_reducible / max(1, report.lines_analyzed)) * 100, 1)} % del archivo)\n"
            f"[bold]Estado:[/bold] {'[green]ACEPTABLE[/green]' if report.is_acceptable else '[red]SOBREINGENIERÍA EXCESIVA[/red]'}"
        )
        console.print(Panel(summary_panel, title="Métricas de Simplicidad Ponytail", border_style=score_color))

        if report.violations:
            table = Table(title="Detalle de Violaciones a la Escalera de la Pereza", border_style="magenta")
            table.add_column("Peldaño", style="bold")
            table.add_column("Regla", style="cyan")
            table.add_column("Ubicación")
            table.add_column("Descripción")
            table.add_column("Recomendación Perezosa (Lazy)", style="green")

            for v in report.violations:
                table.add_row(
                    f"Peldaño {v.rung}",
                    v.name,
                    v.location,
                    v.description,
                    v.lazy_recommendation,
                )
            console.print(table)
        else:
            console.print("[green]✓ Felicitaciones: El código no presenta sobreingeniería según Ponytail.[/green]")

    if fail_on_bloat and not report.is_acceptable:
        if not json_mode:
            console.print(f"\n[bold red]✖ FALLO: El código excede el umbral de sobreingeniería ({report.bloat_score} % > {threshold} %)[/bold red]")
        sys.exit(1)


@cli.command()
@click.argument("proposal")
def debate(proposal: str):
    """Lanza un debate adversarial entre Sombrero Negro y Sombrero Verde moderado por Sombrero Azul."""
    console.print(Panel.fit(f"[bold blue]Debatiendo propuesta arquitectónica:[/bold blue] {proposal}"))

    orchestrator = SixHatsOrchestrator()
    debate_result = asyncio.run(orchestrator.run_debate(proposal))

    # Crítica del Sombrero Negro
    black_table = Table(title="⚫ Objeciones del Sombrero Negro", border_style="red")
    black_table.add_column("Severidad", style="bold red")
    black_table.add_column("Objeción / Riesgo")
    for f in debate_result["black_critique"]:
        black_table.add_row(f["severity"], f["description"])
    console.print(black_table)

    # Alternativas del Sombrero Verde
    green_table = Table(title="🟢 Contrapropuestas del Sombrero Verde", border_style="green")
    green_table.add_column("Alternativa", style="bold green")
    green_table.add_column("Paradigma")
    green_table.add_column("Trade-off")
    for p in debate_result["green_counterproposals"]:
        green_table.add_row(p["name"], p["paradigm"], p["tradeoff"])
    console.print(green_table)

    # Resolución del Sombrero Azul
    res = debate_result["blue_resolution"]
    console.print(
        Panel(
            f"[bold]Veredicto:[/bold] {res['verdict']}\n"
            f"[bold]Síntesis:[/bold] {res['summary']}\n"
            f"[bold]Opción Elegida:[/bold] {res['selected_architecture']}",
            title="🔵 Resolución del Sombrero Azul",
            border_style="cyan",
        )
    )


@cli.command(name="export-tools")
@click.option(
    "--format",
    "-f",
    "format_name",
    type=click.Choice(["openai", "hermes", "hermes-chatml", "claude", "mcp"], case_sensitive=False),
    default="openai",
    help="Formato de salida para esquemas de herramientas.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Ruta de destino opcional para guardar el esquema generado.",
)
def export_tools_cmd(format_name: str, output: str | None):
    """Exporta las herramientas de los 6 Sombreros para Claude, OpenAI Codex, Hermes y entornos Multi-Agente."""
    try:
        content = export_tools_by_format(format_name)
    except Exception as e:
        console.print(f"[bold red]Error exportando herramientas:[/bold red] {e}")
        sys.exit(1)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content + "\n", encoding="utf-8")
        console.print(f"[bold green]✓ Herramientas exportadas exitosamente en formato '{format_name}' a:[/bold green] {output}")
    else:
        click.echo(content)


@cli.group()
def plugin():
    """Gestión e instalación de six-hats como plugin en Claude Code, Cursor, VS Code y Antigravity."""
    pass


@plugin.command(name="install")
@click.argument(
    "target",
    type=click.Choice(["claude", "cursor", "vscode", "antigravity", "all"], case_sensitive=False),
    default="all",
)
@click.option(
    "--scope",
    "-s",
    type=click.Choice(["project", "global"], case_sensitive=False),
    default="project",
    help="Ámbito de instalación: 'project' (directorio actual) o 'global' (directorio de usuario).",
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["uvx", "local"], case_sensitive=False),
    default="uvx",
    help="Método de ejecución: 'uvx' (portátil desde git) o 'local' (entorno python actual).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simula la instalación sin modificar archivos en disco.",
)
def plugin_install(target: str, scope: str, method: str, dry_run: bool):
    """Instala y registra automáticamente el servidor MCP en los clientes especificados."""
    dry_txt = " [Simulación / Dry-run]" if dry_run else ""
    console.print(Panel.fit(f"[bold blue]Instalando six-hats como plugin ({target}){dry_txt}[/bold blue]"))

    results = install_plugin(
        target=target,
        scope=scope,
        method=method,
        cwd=Path.cwd(),
        dry_run=dry_run,
    )

    table = Table(title="Registro de Plugins MCP", border_style="cyan")
    table.add_column("Cliente / Entorno", style="bold")
    table.add_column("Ámbito")
    table.add_column("Método", style="yellow")
    table.add_column("Archivo Configurado", style="dim")
    table.add_column("Estado", style="green")

    for r in results:
        table.add_row(
            r["target"].capitalize(),
            r["scope"],
            r["method"],
            r["filepath"],
            r["action"],
        )

    console.print(table)
    if target in ("claude", "all"):
        console.print("[dim]💡 En Claude Code también puedes usar: [bold]claude mcp add six-hats uvx --from git+https://github.com/elpabloultron/six-hats.git six-hats mcp[/bold][/dim]")


@cli.command()
def mcp():
    """Inicia el servidor MCP estándar en modo STDIO para Antigravity / IDEs."""
    from six_hats.mcp_server import main

    main()


if __name__ == "__main__":
    cli()
