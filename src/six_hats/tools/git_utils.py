import logging
import subprocess
from typing import Tuple, Optional

logger = logging.getLogger("six_hats.git_utils")


def is_git_repository(cwd: Optional[str] = None) -> bool:
    """Verifica si el directorio actual es parte de un repositorio Git."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return res.returncode == 0
    except FileNotFoundError:
        return False


def get_git_diff(filepath: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Obtiene el diff unificado de Git para el directorio o para un archivo específico."""
    cmd = ["git", "diff", "HEAD"]
    if filepath:
        cmd.extend(["--", filepath])

    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout

        # Si HEAD falló (por ejemplo, repo recién inicializado sin commits), probar diff sin HEAD
        cmd_unstaged = ["git", "diff"]
        if filepath:
            cmd_unstaged.extend(["--", filepath])
        res_unstaged = subprocess.run(cmd_unstaged, cwd=cwd, capture_output=True, text=True, check=False)
        return res_unstaged.stdout
    except Exception:
        return ""


def get_file_diff_stats(diff_text: str) -> Tuple[int, int]:
    """Calcula la cantidad de líneas añadidas y eliminadas a partir de un diff unificado."""
    lines_added = 0
    lines_deleted = 0

    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            lines_added += 1
        elif line.startswith("-"):
            lines_deleted += 1

    return lines_added, lines_deleted


def analyze_git_churn(filepath: str, cwd: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Analiza la volatilidad y riesgo histórico del archivo en Git (inspirado en pydriller).

    Retorna: (churn_score, historical_risk)
    """
    if not is_git_repository(cwd):
        return None, None

    try:
        res = subprocess.run(
            ["git", "log", "--follow", "--format=%H|%an", "--", filepath],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return "Archivo nuevo / sin historial previo", "LOW"

        lines = res.stdout.strip().splitlines()
        commit_count = len(lines)
        authors = set()
        for line in lines:
            parts = line.split("|", 1)
            if len(parts) == 2:
                authors.add(parts[1].strip())

        churn_desc = f"{commit_count} commits, {len(authors)} autor(es)"

        if commit_count >= 15 or len(authors) >= 5:
            return f"ZONA CALIENTE ({churn_desc})", "HIGH_HOTSPOT"
        elif commit_count >= 6 or len(authors) >= 3:
            return f"Volatilidad moderada ({churn_desc})", "MEDIUM"
        else:
            return f"Historial estable ({churn_desc})", "LOW"
    except Exception:
        return None, None


def detect_coverage_report(filepath: str, cwd: Optional[str] = None) -> Optional[float]:
    """Busca informes de cobertura estándar (coverage.xml o lcov.info) y extrae el porcentaje del archivo."""
    import os
    import xml.etree.ElementTree as ET

    search_dirs = [cwd or os.getcwd()]
    try:
        parent = os.path.dirname(search_dirs[0])
        if parent and parent != search_dirs[0]:
            search_dirs.append(parent)
    except Exception as err:
        logger.debug("No se pudo obtener directorio padre para búsqueda de cobertura: %s", err)

    target_basename = os.path.basename(filepath)

    for directory in search_dirs:
        # 1. Intentar coverage.xml
        xml_path = os.path.join(directory, "coverage.xml")
        if os.path.isfile(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                for cls in root.iter("class"):
                    cls_file = cls.get("filename", "")
                    if cls_file.endswith(target_basename) or target_basename in cls_file:
                        line_rate = cls.get("line-rate")
                        if line_rate is not None:
                            return round(float(line_rate) * 100.0, 1)
            except Exception as err:
                logger.debug("Error procesando reporte XML de cobertura en %s: %s", xml_path, err)

        # 2. Intentar lcov.info
        lcov_path = os.path.join(directory, "lcov.info")
        if os.path.isfile(lcov_path):
            try:
                with open(lcov_path, "r", encoding="utf-8", errors="ignore") as f:
                    current_file = None
                    lf, lh = 0, 0
                    for line in f:
                        line = line.strip()
                        if line.startswith("SF:"):
                            current_file = line[3:]
                        elif line.startswith("LF:") and current_file and target_basename in current_file:
                            lf = int(line[3:])
                        elif line.startswith("LH:") and current_file and target_basename in current_file:
                            lh = int(line[3:])
                        elif line == "end_of_record" and current_file and target_basename in current_file:
                            if lf > 0:
                                return round((lh / lf) * 100.0, 1)
            except Exception as err:
                logger.debug("Error procesando reporte LCOV de cobertura en %s: %s", lcov_path, err)

    return None
