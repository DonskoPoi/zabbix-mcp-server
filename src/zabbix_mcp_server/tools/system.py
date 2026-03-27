"""
System info tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def apiinfo_version() -> str:
    """Get Zabbix API version information.

    Returns:
        str: JSON formatted API version info
    """
    client = get_zabbix_client()
    result = client.apiinfo.version()
    return format_response(result)
