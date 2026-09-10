"""Motor de análisis sintáctico políglota universal basado en Tree-sitter.

Provee extracción de AST, complejidad ciclomática de McCabe, complejidad cognitiva
y dependencias para Python, TypeScript, JavaScript, Go y Rust.
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Set

try:
    import tree_sitter
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_typescript
    import tree_sitter_go
    import tree_sitter_rust
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


BRANCH_NODE_TYPES = {
    # Condicionales (incluyendo expresiones de Rust)
    "if_statement", "if_expression", "elif_clause", "else_clause", "conditional_expression",
    # Bucles
    "for_statement", "for_expression", "for_in_statement", "while_statement", "while_expression", "loop_expression",
    # Manejo de excepciones
    "except_clause", "catch_clause",
    # Casos y bifurcaciones
    "match_statement", "match_expression", "match_arm", "switch_statement", "switch_expression", "case_statement",
}

SYMBOL_NODE_TYPES = {
    # Python
    "function_definition", "class_definition",
    # JS / TS
    "function_declaration", "method_definition", "class_declaration", "interface_declaration",
    # Go
    "function_declaration", "method_declaration", "type_spec",
    # Rust
    "function_item", "struct_item", "enum_item", "trait_item", "impl_item",
}


def get_parser_for_filename(filename: str):
    """Retorna una instancia de tree_sitter.Parser configurada según la extensión del archivo."""
    if not TREE_SITTER_AVAILABLE:
        return None

    ext = Path(filename).suffix.lower()
    try:
        if ext == ".py":
            lang = tree_sitter.Language(tree_sitter_python.language())
        elif ext in (".js", ".jsx", ".mjs", ".cjs"):
            lang = tree_sitter.Language(tree_sitter_javascript.language())
        elif ext == ".ts":
            lang = tree_sitter.Language(tree_sitter_typescript.language_typescript())
        elif ext == ".tsx":
            lang = tree_sitter.Language(tree_sitter_typescript.language_tsx())
        elif ext == ".go":
            lang = tree_sitter.Language(tree_sitter_go.language())
        elif ext == ".rs":
            lang = tree_sitter.Language(tree_sitter_rust.language())
        else:
            return None

        return tree_sitter.Parser(lang)
    except Exception:
        return None


def extract_node_text(node, source_bytes: bytes) -> str:
    """Extrae el texto del nodo en bytes codificado a string UTF-8."""
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def analyze_tree_sitter(
    code_content: str, filename: str = "source.py"
) -> Optional[Tuple[List[str], int, int, List[str]]]:
    """Analiza código usando Tree-sitter.

    Retorna: (símbolos, complejidad ciclomática, complejidad cognitiva, dependencias).
    """
    parser = get_parser_for_filename(filename)
    if not parser:
        return None

    source_bytes = code_content.encode("utf-8")
    ext = Path(filename).suffix.lower()
    try:
        tree = parser.parse(source_bytes)
    except Exception:
        return None

    symbols: List[str] = []
    dependencies: Set[str] = set()
    cyclomatic_complexity = 1
    cognitive_complexity = 0

    def traverse(node, nesting_level: int = 0):
        nonlocal cyclomatic_complexity, cognitive_complexity

        # 1. Detección de símbolos
        if node.type in SYMBOL_NODE_TYPES:
            name_node = node.child_by_field_name("name")
            if name_node:
                sym_name = extract_node_text(name_node, source_bytes)
                if ext == ".py":
                    prefix = "class" if "class" in node.type else "def"
                elif ext in (".ts", ".js", ".jsx", ".tsx"):
                    prefix = "interface" if "interface" in node.type else ("class" if "class" in node.type else "function")
                elif ext == ".go":
                    prefix = "type" if "type" in node.type else "func"
                elif ext == ".rs":
                    prefix = "struct" if "struct" in node.type else ("fn" if "function" in node.type else "item")
                else:
                    prefix = node.type.split("_")[0]
                symbols.append(f"{prefix} {sym_name}")

        # 2. Detección de dependencias
        if node.type in ("import_statement", "import_from_statement", "use_declaration", "import_declaration"):
            raw_import = extract_node_text(node, source_bytes).strip()
            # Buscar módulos entre comillas (JS, TS, Python, Go)
            quoted = re.findall(r"['\"]([^'\"]+)['\"]", raw_import)
            if quoted:
                for q in quoted:
                    # Limpiar rutas relativas o subrutas (ej. 'react/hooks' -> 'react')
                    dep_name = q.split("/")[0] if not q.startswith(".") else q
                    dependencies.add(dep_name)
            else:
                # Caso sin comillas como Rust 'use std::io;' o Python 'import os'
                words = re.findall(r"[a-zA-Z0-9_]+", raw_import)
                filtered = [w for w in words if w not in ("import", "from", "use", "package", "as")]
                if filtered:
                    dependencies.add(filtered[0])

        # 3. Complejidad ciclomática y cognitiva
        is_branch = node.type in BRANCH_NODE_TYPES
        is_logical_op = False

        if node.type == "binary_expression":
            op_node = node.child_by_field_name("operator")
            if op_node and extract_node_text(op_node, source_bytes) in ("&&", "||", "and", "or"):
                is_logical_op = True

        if is_branch:
            cyclomatic_complexity += 1
            cognitive_complexity += 1 + nesting_level

        if is_logical_op:
            cyclomatic_complexity += 1
            cognitive_complexity += 1

        # Incrementar nivel de anidamiento si este nodo es un bloque o condicional
        new_nesting = nesting_level + (1 if is_branch else 0)

        for child in node.children:
            traverse(child, new_nesting)

    traverse(tree.root_node)

    return symbols, max(1, cyclomatic_complexity), cognitive_complexity, sorted(list(dependencies))
