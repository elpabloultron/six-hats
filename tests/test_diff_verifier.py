import pytest
from six_hats.tools.diff_generator import (
    validate_patch_syntax,
    apply_patch_in_memory,
    generate_and_verify_patch,
    clean_code_block,
    synthesize_heuristic_refactor,
)


def test_clean_code_block():
    """Verifica la eliminación de delimitadores de código markdown."""
    raw = "```python\ndef test(): pass\n```"
    assert clean_code_block(raw) == "def test(): pass"

    plain = "def test(): pass"
    assert clean_code_block(plain) == plain


def test_validate_patch_syntax():
    """Verifica la validación de sintaxis Python mediante ast.parse."""
    valid_code = "def correcto():\n    return 42\n"
    is_valid, err = validate_patch_syntax(valid_code, "test.py")
    assert is_valid is True
    assert err is None

    invalid_code = "def roto(:\n    return 42\n"
    is_valid, err = validate_patch_syntax(invalid_code, "test.py")
    assert is_valid is False
    assert err is not None
    assert "sintaxis" in err.lower() or "syntax" in err.lower()

    # Archivo no Python se asume válido
    is_valid, err = validate_patch_syntax("{\"clave\": 1}", "test.json")
    assert is_valid is True


def test_apply_patch_in_memory():
    """Verifica la aplicación en memoria de un diff unificado sobre el código original."""
    original = "def foo():\n    return 1\n"
    patch = (
        "--- a/test.py\n"
        "+++ b/test.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def foo():\n"
        "-    return 1\n"
        "+    return 2\n"
    )
    success, patched, err = apply_patch_in_memory(original, patch)
    assert success is True
    assert patched == "def foo():\n    return 2\n"


def test_generate_and_verify_patch_fallback():
    """Verifica que si la refactorización propuesta contiene error sintáctico, se aplique el fallback seguro."""
    original = "def peligroso(cmd):\n    eval(cmd)\n"
    bad_refactor = "def peligroso(cmd):\n    eval(cmd roto(\n"

    patch, is_valid, err = generate_and_verify_patch(
        original_code=original,
        filepath="peligro.py",
        refactored_code=bad_refactor,
        applied_mitigations=["Invocación dinámica mitigada"],
    )

    assert is_valid is True
    assert "Fallback aplicado" in str(err)
    assert "MITIGACION SOMBRERO AZUL" in patch
