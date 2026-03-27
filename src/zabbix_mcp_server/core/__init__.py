"""
Core module for Zabbix MCP Server.
"""

from .client import get_zabbix_client, zabbix_api
from .config import (
    get_transport_config_readonly,
    get_transport_config_writable,
    get_auth_provider,
)
from .utils import format_response
from .tool_registry import (
    readonly_tool,
    writable_tool,
    register_readonly_tools,
    register_writable_tools,
    get_registered_readonly_count,
    get_registered_writable_count,
)

__all__ = [
    "get_zabbix_client",
    "zabbix_api",
    "get_transport_config_readonly",
    "get_transport_config_writable",
    "get_auth_provider",
    "format_response",
    "readonly_tool",
    "writable_tool",
    "register_readonly_tools",
    "register_writable_tools",
    "get_registered_readonly_count",
    "get_registered_writable_count",
]
