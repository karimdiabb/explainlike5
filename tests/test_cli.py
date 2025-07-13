from click.testing import CliRunner
from explainlike5.cli import main

def test_cli_outputs_alive_message():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Explainlike5 is alive" in result.output

