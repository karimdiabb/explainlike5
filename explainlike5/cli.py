import click
from explainlike5.llm import (
    explain_with_openrouter,
    comment_with_openrouter,
)
from explainlike5.core import (
    find_functions,
    extract_function_code,
    add_docstring_to_function,
)


@click.command()
@click.argument("file")
@click.option("--function", "-f", help="Function name")
@click.option("--comment", is_flag=True, help="Generate a docstring")
@click.option(
    "--write",
    is_flag=True,
    help="Overwrite original function with the commented version",
)
def main(file, function, comment, write):
    click.echo(f"📄 File: {file}")

    if not function:
        return list_functions(file)

    click.echo(f"🔍 Function: {function}")
    code, error = extract_function_code(file, function)
    if error:
        return click.echo(f"❌ {error}")

    if comment:
        return handle_comment(code, file, function, write)

    return handle_explanation(code)


def list_functions(file):
    click.echo("🔎 Listing functions...")
    for name in find_functions(file):
        click.echo(f"• {name}")


def handle_comment(code, file, function, write):
    result, err = comment_with_openrouter(code)
    if err:
        return click.echo(f"❌ LLM error: {err}")

    if write:
        success = add_docstring_to_function(file, function, result)
        if success:
            click.echo(f"✅ Comment written to {file}")
        else:
            click.echo("❌ Failed to write comment.")
    else:
        click.echo("📝 Commented function:\n")
        click.echo(result)


def handle_explanation(code):
    result, err = explain_with_openrouter(code)
    if err:
        return click.echo(f"❌ LLM error: {err}")
    click.echo("🧠 Explanation:\n")
    click.echo(result)
