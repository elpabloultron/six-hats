import pytest
from six_hats.tools.ast_extractor import extract_ast_data, extract_ast_from_python
from six_hats.tools.cognitive_metrics import (
    calculate_cognitive_complexity,
    calculate_maintainability_index,
)
from six_hats.tools.tree_sitter_engine import (
    analyze_tree_sitter,
    get_parser_for_filename,
)
from six_hats.tools.git_utils import get_file_diff_stats


SAMPLE_NESTED_CODE = """
def complejo(x, y, z):
    if x > 0:
        if y > 0:
            for i in range(10):
                if z and (x or y):
                    while x < 100:
                        x += 1
    elif x < 0:
        try:
            val = 1 / x
        except ZeroDivisionError:
            pass
    return x
"""

SAMPLE_JS_CODE = """
function calcularTotal(items) {
    let total = 0;
    for (let i = 0; i < items.length; i++) {
        if (items[i].precio > 0) {
            total += items[i].precio;
        }
    }
    return total;
}
"""


def test_cognitive_complexity_deep_nesting():
    """Verifica el cálculo de complejidad cognitiva en funciones con alto anidamiento."""
    cog = calculate_cognitive_complexity(SAMPLE_NESTED_CODE)
    assert cog >= 7

    symbols, mccabe, deps = extract_ast_from_python(SAMPLE_NESTED_CODE)
    assert mccabe >= 5
    assert "def complejo" in symbols

    mi = calculate_maintainability_index(SAMPLE_NESTED_CODE, mccabe)
    assert 0.0 <= mi <= 100.0


def test_ast_extractor_with_diff_stats():
    """Verifica extract_ast_data con estadísticas de git diff y dependencias."""
    code = (
        "import json\n"
        "from os import path\n"
        "class Gestor:\n"
        "    def procesar(self):\n"
        "        pass\n"
    )
    data = extract_ast_data(code, lines_added=5, lines_deleted=1, filename="gestor.py")
    assert data.lines_added == 5
    assert data.lines_deleted == 1
    assert "class Gestor" in data.symbols_affected
    assert "json" in data.dependencies or "os" in data.dependencies


def test_tree_sitter_engine_polyglot():
    """Verifica la detección de lenguaje y extracción de métricas con tree-sitter."""
    parser_js = get_parser_for_filename("app.js")
    parser_py = get_parser_for_filename("main.py")
    parser_go = get_parser_for_filename("main.go")

    assert parser_js is not None or parser_py is not None

    ast_res = analyze_tree_sitter(SAMPLE_JS_CODE, filename="app.js")
    if ast_res:
        symbols, cyclomatic, cognitive, deps = ast_res
        assert cyclomatic >= 1
        assert any("calcularTotal" in s for s in symbols)


def test_git_utils_diff_stats():
    """Verifica el cómputo de líneas añadidas y eliminadas en formato unified diff."""
    patch_text = (
        "--- a/test.py\n"
        "+++ b/test.py\n"
        "@@ -1,3 +1,4 @@\n"
        " linea1\n"
        "-linea2_eliminada\n"
        "+linea2_nueva\n"
        "+linea3_nueva\n"
        " linea4\n"
    )
    added, deleted = get_file_diff_stats(patch_text)
    assert added == 2
    assert deleted == 1
