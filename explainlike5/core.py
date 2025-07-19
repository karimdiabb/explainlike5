import ast
import re


def find_functions(file):
    with open(file, "r") as f:
        content = f.read()

    tree = ast.parse(content)
    functions = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    return functions


def extract_function_code(file, function):
    with open(file, "r") as f:
        content = f.read()

    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            return ast.get_source_segment(content, node), None

    return None, f"Function '{function}' not found."


def add_comment_to_function(file, function, new_code):
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tree = ast.parse("".join(lines))

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            start = node.lineno - 1
            end = node.end_lineno

            new_lines = [line + "\n" for line in new_code.strip().splitlines()]
            lines[start:end] = new_lines

            with open(file, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True

    return False


def add_docstring_to_function(file, function_name, raw_docstring):
    doc = sanitize_docstring(raw_docstring)

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out, inserted = [], False
    pattern = re.compile(
        rf"^(?P<indent>\s*)def\s+{re.escape(function_name)}\s*\(.*\)\s*:"
    )

    for line in lines:
        out.append(line)
        if not inserted:
            m = pattern.match(line)
            if m:
                indent = m.group("indent") + "    "
                out.append(f'{indent}"""\n')
                for ln in doc.splitlines():
                    out.append(f"{indent}{ln}\n")
                out.append(f'{indent}"""\n')
                inserted = True

    if not inserted:
        return False

    with open(file, "w", encoding="utf-8") as f:
        f.writelines(out)
    return True


def sanitize_docstring(text: str) -> str:
    text = text.strip()
    text = text.replace("```python", "").replace("```", "").replace("`", "")

    text = _find_function_start(text)

    docstring = _extract_docstring_with_ast(text)
    if docstring:
        return docstring

    text = _manual_cleanup(text)
    return text.strip().strip("'\"")


def _find_function_start(text: str) -> str:
    """Find text starting from function definition."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            return "\n".join(lines[i:])
    return text


def _extract_docstring_with_ast(text: str) -> str:
    """Extract docstring using AST parsing."""
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    return node.body[0].value.value.strip()
    except (SyntaxError, ValueError):
        pass
    return ""


def _manual_cleanup(text: str) -> str:
    """Manual cleanup when AST parsing fails."""
    lines = text.splitlines()
    cleaned = []
    for ln in lines:
        stripped = ln.strip()
        if stripped.lower() == "python" or stripped.startswith("def "):
            continue
        cleaned.append(ln)

    text = "\n".join(cleaned).strip()

    if (text.startswith('"""') and text.endswith('"""')) or (
        text.startswith("'''") and text.endswith("'''")
    ):
        text = text[3:-3].strip()

    return text
