"""Generador determinista de parches reales en formato Unified Diff (difflib).

Produce parches unificados estándar compatibles con «git apply» y «patch -p1».
"""

import difflib
import re
from typing import List, Optional


def clean_code_block(text: str) -> str:
    """Remueve bloques de markdown (```python ... ```) si el modelo los incluye."""
    pattern = re.compile(r"^```[a-zA-Z0-9_\-]*\n(.*?)\n```$", re.DOTALL)
    match = pattern.search(text.strip())
    if match:
        return match.group(1)
    return text


def synthesize_heuristic_refactor(original_code: str, applied_mitigations: List[str]) -> str:
    """Genera una versión refactorizada del código real aplicando mitigaciones concretas."""
    lines = original_code.splitlines()
    refactored: List[str] = []

    # Verificar si se requiere agregar import pathlib
    needs_pathlib = any("pathlib" in m.lower() for m in applied_mitigations) and "from pathlib import Path" not in original_code
    if needs_pathlib:
        refactored.append("from pathlib import Path")

    for line in lines:
        # Mitigar eval() o exec()
        if "eval(" in line or "exec(" in line:
            indent = len(line) - len(line.lstrip())
            refactored.append(f"{' ' * indent}# MITIGACION SOMBRERO AZUL: Invocacion dinamica deshabilitada por seguridad")
            refactored.append(f"{' ' * indent}# {line.strip()}")
            refactored.append(f"{' ' * indent}resultado_seguro = {{'status': 'sanitized', 'input': str(comando if 'comando' in locals() else '')}}")
            continue

        # Mitigar shell=True
        if "shell=True" in line:
            line = line.replace("shell=True", "shell=False")

        # Mitigar except: pass
        if re.search(r"except\s*:\s*pass", line) or re.search(r"except\s+Exception\s*:\s*pass", line):
            indent = len(line) - len(line.lstrip())
            refactored.append(f"{' ' * indent}except Exception as exc:")
            refactored.append(f"{' ' * (indent + 4)}# Log defensivo de excepcion")
            refactored.append(f"{' ' * (indent + 4)}import logging; logging.warning(f'Error controlado: {{exc}}')")
            continue

        refactored.append(line)

    return "\n".join(refactored) + ("\n" if original_code.endswith("\n") else "")


def generate_real_patch(
    original_code: str,
    filepath: str = "solucion.py",
    refactored_code: Optional[str] = None,
    applied_mitigations: Optional[List[str]] = None,
) -> str:
    """Genera un diff unificado real entre el código original y el código refactorizado."""
    if refactored_code is None:
        refactored_code = synthesize_heuristic_refactor(original_code, applied_mitigations or [])

    refactored_code = clean_code_block(refactored_code)

    orig_lines = original_code.splitlines(keepends=True)
    refac_lines = refactored_code.splitlines(keepends=True)

    fromfile = f"a/{filepath}"
    tofile = f"b/{filepath}"

    diff = difflib.unified_diff(
        orig_lines,
        refac_lines,
        fromfile=fromfile,
        tofile=tofile,
        n=3,
    )
    result = "".join(diff)
    return result if result.strip() else ""
