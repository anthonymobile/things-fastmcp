"""Shared fixtures. Tests never require Things 3 to be running."""
import pytest

from things_mcp import fast_server


@pytest.fixture
def server():
    """The module-level MCPServer instance."""
    return fast_server.mcp
