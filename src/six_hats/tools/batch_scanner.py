"""Motor de escaneo recursivo por lotes (Batch Scanner) para auditorías de repositorios completos.

Analiza directorios enteros en paralelo mediante semáforos asíncronos, agregando métricas
de complejidad, seguridad, experiencia de desarrollo y sobreingeniería de Ponytail.
"""

import asyncio
import os
from pathlib import Path
from typing import Any, List, Optional, Set
from pydantic import BaseModel, Field

from six_hats.core.orchestrator import SixHatsOrchestrator
from six_hats.core.models import SixHatsReviewResult

DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "site-packages",
    ".idea",
    ".vscode",
    "target",
    "vendor",
    ".gemini",
}

SUPPORTED_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
}


class FileScanSummary(BaseModel):
    """Resumen de análisis de un archivo individual en el escaneo por lotes."""
    filepath: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float
    bloat_score: float
    critical_findings_count: int
    high_findings_count: int
    verdict: str
    selected_architecture: str
    result: Optional[SixHatsReviewResult] = None


class BatchScanReport(BaseModel):
    """Informe consolidado de escaneo sobre un repositorio o árbol de directorios."""
    directory: str
    total_files_scanned: int
    total_lines_analyzed: int
    avg_cyclomatic_complexity: float
    avg_cognitive_complexity: float
    avg_maintainability_index: float
    avg_bloat_score: float
    critical_vulnerabilities_count: int
    high_vulnerabilities_count: int
    hotspots: List[dict[str, Any]] = Field(default_factory=list)
    file_summaries: List[FileScanSummary] = Field(default_factory=list)


def discover_source_files(
    directory: str | Path,
    max_files: int = 200,
    ignored_dirs: Optional[Set[str]] = None,
    extensions: Optional[Set[str]] = None,
) -> List[Path]:
    """Descubre archivos fuente analizables ignorando carpetas de dependencias y temporales."""
    base_path = Path(directory).resolve()
    ignore = ignored_dirs or DEFAULT_IGNORED_DIRS
    exts = extensions or SUPPORTED_EXTENSIONS

    discovered: List[Path] = []

    for root, dirs, files in os.walk(base_path):
        # Filtrar directorios ignorados en tiempo de recorrido
        dirs[:] = [d for d in dirs if d not in ignore and not d.startswith(".")]

        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in exts and not f.startswith("."):
                discovered.append(p)
                if len(discovered) >= max_files:
                    return discovered

    return discovered


async def scan_single_file(
    filepath: Path,
    base_dir: Path,
    orchestrator: SixHatsOrchestrator,
    semaphore: asyncio.Semaphore,
) -> Optional[FileScanSummary]:
    """Escanea un único archivo con concurrencia controlada."""
    async with semaphore:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            if not content.strip():
                return None

            rel_path = str(filepath.relative_to(base_dir))
            review = await orchestrator.run_full_cycle(
                code_content=content,
                is_diff=False,
                filepath=rel_path,
            )

            crit_count = sum(1 for f in review.black if f.severity == "CRITICAL")
            high_count = sum(1 for f in review.black if f.severity == "HIGH")

            return FileScanSummary(
                filepath=rel_path,
                cyclomatic_complexity=review.white.cyclomatic_complexity,
                cognitive_complexity=review.white.cognitive_complexity,
                maintainability_index=review.white.maintainability_index,
                bloat_score=review.red.bloat_score,
                critical_findings_count=crit_count,
                high_findings_count=high_count,
                verdict=review.consensus.verdict,
                selected_architecture=review.consensus.selected_architecture,
                result=review,
            )
        except Exception:
            return None


async def run_batch_scan(
    directory: str | Path,
    concurrency: int = 4,
    max_files: int = 200,
    orchestrator: Optional[SixHatsOrchestrator] = None,
) -> BatchScanReport:
    """Ejecuta el escaneo concurrente de todos los archivos del directorio."""
    base_dir = Path(directory).resolve()
    files = discover_source_files(base_dir, max_files=max_files)

    orch = orchestrator or SixHatsOrchestrator()
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [scan_single_file(p, base_dir, orch, semaphore) for p in files]
    results = await asyncio.gather(*tasks)

    summaries = [s for s in results if s is not None]

    total_files = len(summaries)
    if total_files == 0:
        return BatchScanReport(
            directory=str(base_dir),
            total_files_scanned=0,
            total_lines_analyzed=0,
            avg_cyclomatic_complexity=0.0,
            avg_cognitive_complexity=0.0,
            avg_maintainability_index=100.0,
            avg_bloat_score=0.0,
            critical_vulnerabilities_count=0,
            high_vulnerabilities_count=0,
            hotspots=[],
            file_summaries=[],
        )

    total_lines = sum(s.result.white.lines_added if s.result else 0 for s in summaries)
    avg_cyc = round(sum(s.cyclomatic_complexity for s in summaries) / total_files, 2)
    avg_cog = round(sum(s.cognitive_complexity for s in summaries) / total_files, 2)
    avg_mi = round(sum(s.maintainability_index for s in summaries) / total_files, 2)
    avg_bloat = round(sum(s.bloat_score for s in summaries) / total_files, 2)
    crit_total = sum(s.critical_findings_count for s in summaries)
    high_total = sum(s.high_findings_count for s in summaries)

    # Identificación de Hotspots (archivos con mayor riesgo o sobreingeniería)
    sorted_by_risk = sorted(
        summaries,
        key=lambda s: (s.critical_findings_count * 10 + s.high_findings_count * 5 + s.cognitive_complexity + s.bloat_score),
        reverse=True,
    )

    hotspots = [
        {
            "filepath": s.filepath,
            "verdict": s.verdict,
            "critical": s.critical_findings_count,
            "high": s.high_findings_count,
            "cognitive": s.cognitive_complexity,
            "bloat": s.bloat_score,
        }
        for s in sorted_by_risk[:8]
    ]

    return BatchScanReport(
        directory=str(base_dir),
        total_files_scanned=total_files,
        total_lines_analyzed=total_lines,
        avg_cyclomatic_complexity=avg_cyc,
        avg_cognitive_complexity=avg_cog,
        avg_maintainability_index=avg_mi,
        avg_bloat_score=avg_bloat,
        critical_vulnerabilities_count=crit_total,
        high_vulnerabilities_count=high_total,
        hotspots=hotspots,
        file_summaries=summaries,
    )
