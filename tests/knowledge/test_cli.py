import pytest
from cli.knowledge import get_client

def test_cli_client_initialization():
    client = get_client()
    assert client.knowledge is not None
