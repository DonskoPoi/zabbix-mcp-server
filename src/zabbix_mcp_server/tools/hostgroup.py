"""
Host group management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def hostgroup_get(groupids: Optional[List[str]] = None,
                  output: Union[str, List[str]] = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None) -> str:
    """Get host groups from Zabbix.

    Args:
        groupids: List of group IDs to retrieve
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of host groups
    """
    client = get_zabbix_client()
    params = {"output": output}

    if groupids:
        params["groupids"] = groupids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.hostgroup.get(**params)
    return format_response(result)


@writable_tool()
def hostgroup_create(name: str) -> str:
    """Create a new host group in Zabbix.

    Args:
        name: Host group name

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    result = client.hostgroup.create(name=name)
    return format_response(result)


@writable_tool()
def hostgroup_update(groupid: str, name: str) -> str:
    """Update an existing host group in Zabbix.

    Args:
        groupid: Group ID to update
        name: New group name

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    result = client.hostgroup.update(groupid=groupid, name=name)
    return format_response(result)


@writable_tool()
def hostgroup_delete(groupids: List[str]) -> str:
    """Delete host groups from Zabbix.

    Args:
        groupids: List of group IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.hostgroup.delete(*groupids)
    return format_response(result)
