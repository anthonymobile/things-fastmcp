"""
Minimal test suite for the Things MCP server on MCP SDK 2.x.

Uses the SDK's in-process client (``mcp.Client(server)``) so no subprocess and
no Things 3 installation is needed; ``things-py`` is mocked where a tool would
otherwise hit the Things database.
"""
from unittest.mock import patch

import pytest
from mcp import Client
from mcp.server.mcpserver import MCPServer

from things_mcp import fast_server

EXPECTED_TOOLS = {
    # list views
    "get-inbox", "get-today", "get-upcoming", "get-anytime", "get-someday",
    "get-logbook", "get-trash",
    # basic operations
    "get-todos", "get-projects", "get-areas",
    # tags
    "get-tags", "get-tagged-items",
    # search
    "search-todos", "search-advanced",
    # modification / URL scheme
    "add-todo", "add-project", "update-todo", "update-project",
    "show-item", "search-items",
    # misc
    "get-recent", "get-cache-stats",
}


def test_server_module_imports(server):
    assert isinstance(server, MCPServer)
    assert server.name == "Things"


async def test_list_tools_exposes_all_22_tools(server):
    async with Client(server) as client:
        result = await client.list_tools()
    names = {t.name for t in result.tools}
    assert len(result.tools) == 22
    assert names == EXPECTED_TOOLS


async def test_tool_argument_schemas_are_preserved(server):
    """Spot-check that argument names/defaults survived the SDK port."""
    async with Client(server) as client:
        result = await client.list_tools()
    by_name = {t.name: t for t in result.tools}

    logbook = by_name["get-logbook"].input_schema
    assert logbook["properties"]["period"]["default"] == "7d"
    assert logbook["properties"]["limit"]["default"] == 50

    add_todo = by_name["add-todo"].input_schema
    assert add_todo["required"] == ["title"]
    assert set(add_todo["properties"]) == {
        "title", "notes", "when", "deadline", "tags", "checklist_items",
        "list_id", "list_title", "heading",
    }


SAMPLE_TODO = {
    "uuid": "ABC123",
    "type": "to-do",
    "title": "Write the migration PR",
    "status": "incomplete",
    "notes": "Port to SDK 2.x",
    "start": "Anytime",
    "start_date": None,
    "deadline": "2026-11-15",
    "tags": ["work"],
    "checklist": False,
}


async def test_get_inbox_round_trip_with_mocked_things(server):
    """Round-trip a read-only tool through the client with things-py mocked."""
    with patch.object(fast_server.things, "inbox", return_value=[SAMPLE_TODO]) as inbox:
        async with Client(server) as client:
            result = await client.call_tool("get-inbox", {})

    inbox.assert_called_once_with()
    assert result.is_error is not True
    text = "".join(block.text for block in result.content if block.type == "text")
    assert "Write the migration PR" in text
    assert "ABC123" in text


async def test_get_inbox_empty(server):
    with patch.object(fast_server.things, "inbox", return_value=[]):
        async with Client(server) as client:
            result = await client.call_tool("get-inbox", {})
    text = "".join(block.text for block in result.content if block.type == "text")
    assert text == "No items found in Inbox"
