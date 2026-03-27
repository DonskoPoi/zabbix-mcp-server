"""
Zabbix MCP Server - A Model Context Protocol server for Zabbix integration.
"""

# Version info
__version__ = "2.0.0"

# Export core functionality
from .core import (
    get_zabbix_client,
    zabbix_api,
    get_transport_config_readonly,
    get_transport_config_writable,
    format_response,
    readonly_tool,
    writable_tool,
    register_readonly_tools,
    register_writable_tools,
    get_registered_readonly_count,
    get_registered_writable_count,
)

__all__ = [
    # Core
    "get_zabbix_client",
    "zabbix_api",
    "get_transport_config_readonly",
    "get_transport_config_writable",
    "format_response",
    "readonly_tool",
    "writable_tool",
    "register_readonly_tools",
    "register_writable_tools",
    "get_registered_readonly_count",
    "get_registered_writable_count",
    # Version
    "__version__",
]
