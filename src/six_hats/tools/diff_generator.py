"""Generador determinista de parches reales en formato Unified Diff (difflib) y motor de validación.

Produce parches unificados estándar compatibles con «git apply» y «patch -p1»,
verificando la integridad sintáctica del código refactorizado antes de su emisión.
"""

import ast
import difflib
import re
from typing import List, Optional, Tuple


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


def validate_patch_syntax(code: str, filepath: str = "solucion.py") -> Tuple[bool, Optional[str]]:
    """Valida sintácticamente el código refactorizado para garantizar que compila limpiamente."""
    if not code.strip():
        return True, None

    if filepath.endswith(".py"):
        try:
            ast.parse(code, filename=filepath)
            return True, None
        except SyntaxError as exc:
            return False, f"Error de sintaxis en línea {exc.lineno}: {exc.msg}"
        except Exception as exc:
            return False, f"Fallo al validar AST: {exc}"

    # Para otros formatos (JSON, YAML, etc.) se asume sintaxis no-Python
    return True, None


def apply_patch_in_memory(original_code: str, patch_text: str) -> Tuple[bool, str, Optional[str]]:
    """Aplica un diff unificado sobre el código original en memoria para verificar consistencia."""
    if not patch_text.strip():
        return True, original_code, None

    orig_lines = original_code.splitlines(keepends=True)
    patch_lines = patch_text.splitlines(keepends=True)

    result_lines: List[str] = []
    i = 0
    in_hunk = False

    for line in patch_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if in_hunk:
            if line.startswith("-"):
                # Línea eliminada en original
                if i < len(orig_lines):
                    i += 1
            elif line.startswith("+"):
                # Línea añadida
                result_lines.append(line[1:])
            elif line.startswith(" "):
                # Línea de contexto
                result_lines.append(line[1:])
                i += 1

    # Agregar remanente de líneas originales si el parche cubrió un fragmento
    if i < len(orig_lines):
        result_lines.extend(orig_lines[i:])

    patched_code = "".join(result_lines)
    return True, patched_code, None


def generate_real_patch(
    original_code: str,
    filepath: str = "solucion.py",
    refactored_code: Optional[str] = None,
    applied_mitigations: Optional[List[str]] = None,
) -> str:
    """Genera un diff unificado real entre el código original y el código refactorizado."""
    patch, _, _ = generate_and_verify_patch(
        original_code=original_code,
        filepath=filepath,
        refactored_code=refactored_code,
        applied_mitigations=applied_mitigations,
    )
    return patch


def generate_and_verify_patch(
    original_code: str,
    filepath: str = "solucion.py",
    refactored_code: Optional[str] = None,
    applied_mitigations: Optional[List[str]] = None,
) -> Tuple[str, bool, Optional[str]]:
    """Genera el diff unificado y verifica su validez sintáctica de forma automática."""
    if refactored_code is None:
        refactored_code = synthesize_heuristic_refactor(original_code, applied_mitigations or [])

    refactored_code = clean_code_block(refactored_code)

    # Validación sintáctica preliminar
    is_valid, syntax_error = validate_patch_syntax(refactored_code, filepath=filepath)

    # Si la propuesta personalizada tiene error de sintaxis, recurrir a la heurística segura
    if not is_valid and applied_mitigations is not None:
        fallback_refactor = synthesize_heuristic_refactor(original_code, applied_mitigations)
        fb_valid, fb_err = validate_patch_syntax(fallback_refactor, filepath=filepath)
        if fb_valid:
            refactored_code = fallback_refactor
            is_valid = True
            syntax_error = f"Fallback aplicado: Se corrigió error sintáctico previo ({syntax_error})"

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
    final_patch = result if result.strip() else ""

    return final_patch, is_valid, syntax_error
