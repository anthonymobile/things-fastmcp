# Changelog

All notable changes to Things 3 Enhanced MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-09

### Changed
- **Ported to the MCP Python SDK 2.x** (`mcp>=2,<3`). The server is now built on
  `mcp.server.mcpserver.MCPServer`, the 2.x successor to `FastMCP`
  (`mcp.server.fastmcp` no longer exists in 2.x). Tool names, argument schemas
  and behaviour are unchanged; existing prompts keep working.
- Single implementation and single entry point: the package installs a
  `things-mcp` console script (`things_mcp.fast_server:run_things_mcp_server`)
  that runs the server over stdio with no arguments, so Claude Desktop can be
  configured with `"command": "<repo>/.venv/bin/things-mcp"`.
- Console logging is explicitly bound to stderr; stdout is reserved for the
  stdio transport. File logs remain under `~/.things-mcp/logs/`.
- `configure_token.py` imports from the installed `things_mcp` package instead
  of the `src.` path.
- pytest configuration moved from `pytest.ini` into `pyproject.toml`
  (`asyncio_mode = "auto"`); `pytest-asyncio` added to the `dev` extra.

### Added
- `tests/` — a minimal pytest suite that uses the SDK's in-process client
  (`mcp.Client(server)`) to assert all 22 tools are listed and to round-trip
  `get-inbox` with `things-py` mocked. Does not need Things 3 running.
- `scripts/smoke_test.py` — stdio handshake + `tools/list` check against the
  installed console script (pure Python, works on macOS without GNU `timeout`).
- `setup.sh` — builds the venv with uv (Python 3.12), installs the package,
  stores the Things auth token if missing, runs the smoke test and prints the
  Claude Desktop config block.

### Removed
- The parallel low-level `mcp.server.Server` implementation: root
  `things_server.py`, `src/things_mcp/things_server.py`, `simple_server.py`,
  `mcp_tools.py`, and the `handlers.py` / `tag_handler.py` modules that only it
  used.
- Root `things_fast_server.py` wrapper (superseded by the console script),
  `smithery.yaml`, and the unused `httpx` dependency.

## [1.0.0] - 2025-05-30

### Added
- 🚀 **FastMCP Implementation**: Complete rewrite using FastMCP pattern for better maintainability
- 🔄 **Reliability Features**:
  - Circuit breaker pattern to prevent cascading failures
  - Exponential backoff retry logic for transient failures
  - Dead letter queue for failed operations
- ⚡ **Performance Optimizations**:
  - Intelligent caching system with TTL management
  - Rate limiting to prevent overwhelming Things app
  - Automatic cache invalidation on data modifications
- 🍎 **AppleScript Bridge**: Fallback mechanism when URL schemes fail
- 📊 **Enhanced Monitoring**:
  - Structured JSON logging
  - Performance metrics and statistics
  - Comprehensive error tracking
  - Debug-friendly output
- 🛡️ **Error Handling**: Comprehensive exception management and recovery
- 🧪 **Test Suite**: Extensive tests for reliability
- 📦 **Smithery Support**: Full configuration for Smithery registry deployment
- 📝 **Documentation**: Enhanced README with detailed setup and troubleshooting guides

### Changed
- Rebranded to "Things 3 Enhanced MCP" for clear differentiation
- Updated package name to `things3-enhanced-mcp`
- Improved configuration token handling
- Enhanced URL scheme operations with better error recovery

### Fixed
- Token configuration import issues
- URL scheme reliability problems
- Various edge cases in task/project operations

### Attribution
Based on the original [things-mcp](https://github.com/hald/things-mcp) by Harald Lindstrøm

[1.0.0]: https://github.com/excelsier/things-fastmcp/releases/tag/v1.0.0 