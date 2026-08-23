"""CLI entry point wrapper for Data Governance Platform."""

from cli.commands.data_governance import add_data_governance_parser, handle_data_governance_command

__all__ = ["add_data_governance_parser", "handle_data_governance_command"]
