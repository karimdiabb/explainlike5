import ast


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
