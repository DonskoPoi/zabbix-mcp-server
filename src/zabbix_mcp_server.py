#!/usr/bin/env python3
"""
Zabbix MCP Server - Backwards compatibility wrapper.

This file provides backwards compatibility for existing imports.
Please use the new modular structure instead:

- from zabbix_mcp_server.main import mcp, main
- from zabbix_mcp_server.core import get_zabbix_client, is_read_only, etc.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "The zabbix_mcp_server.py monolithic file is deprecated. "
    "Please use the new modular structure: 'from zabbix_mcp_server.main import mcp, main'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the new package
from zabbix_mcp_server import (
    __version__,
    # Core
    get_zabbix_client,
    zabbix_api,
    is_read_only,
    get_transport_config,
    format_response,
    validate_read_only,
    # Main
    mcp,
    main,
    # Tools
    register_all_tools,
)

__all__ = [
    # Core
    "get_zabbix_client",
    "zabbix_api",
    "is_read_only",
    "get_transport_config",
    "format_response",
    "validate_read_only",
    # Main
    "mcp",
    "main",
    # Tools
    "register_all_tools",
    # Version
    "__version__",
]

if __name__ == "__main__":
    main()
