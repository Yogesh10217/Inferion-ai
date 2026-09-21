"""Integration tests for Identity CLI commands."""

from click.testing import CliRunner

from cli.commands.identity import identity_cli


def test_identity_cli_commands():
    runner = CliRunner()

    res_list = runner.invoke(identity_cli, ["list", "--tenant-id", "t_cli"])
    assert res_list.exit_code == 0
    assert "t_cli" in res_list.output

    res_jit = runner.invoke(
        identity_cli, ["privileged-access", "--identity-id", "id_admin", "--role", "SECURITY_ADMIN"]
    )
    assert res_jit.exit_code == 0
    assert "REQUESTED" in res_jit.output
