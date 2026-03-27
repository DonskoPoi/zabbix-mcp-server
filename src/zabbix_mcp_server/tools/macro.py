"""
Macro management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def usermacro_get(globalmacroids: Optional[List[str]] = None,
                  hostids: Optional[List[str]] = None,
                  output: Union[str, List[str]] = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None) -> str:
    """Get global macros from Zabbix with optional filtering.

    Args:
        globalmacroids: List of global macro IDs to retrieve
        hostids: List of host IDs to filter by (for host macros)
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of global macros
    """
    client = get_zabbix_client()
    params = {"output": output}

    if globalmacroids:
        params["globalmacroids"] = globalmacroids
    if hostids:
        params["hostids"] = hostids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.usermacro.get(**params)
    return format_response(result)
