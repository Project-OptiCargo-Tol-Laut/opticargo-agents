from opticargo_agents.cli.doctor import main


def test_doctor_command_exits_successfully(capsys) -> None:
    assert main() == 0
    output = capsys.readouterr().out
    assert "opticargo-agents" in output
