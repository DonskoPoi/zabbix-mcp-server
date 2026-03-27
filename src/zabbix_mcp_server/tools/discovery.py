"""
Discovery rule management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def discoveryrule_get(itemids: Optional[List[str]] = None,
                      hostids: Optional[List[str]] = None,
                      templateids: Optional[List[str]] = None,
                      output: Union[str, List[str]] = "extend",
                      search: Optional[Dict[str, str]] = None,
                      filter: Optional[Dict[str, Any]] = None) -> str:
    """Get discovery rules from Zabbix with optional filtering.

    Args:
        itemids: List of discovery rule IDs to retrieve
        hostids: List of host IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of discovery rules
    """
    client = get_zabbix_client()
    params = {"output": output}

    if itemids:
        params["itemids"] = itemids
    if hostids:
        params["hostids"] = hostids
    if templateids:
        params["templateids"] = templateids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.discoveryrule.get(**params)
    return format_response(result)
