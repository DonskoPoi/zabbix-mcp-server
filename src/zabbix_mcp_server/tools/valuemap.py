"""
Value map management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def valuemap_get(valuemapids: Optional[List[str]] = None,
                 search: Optional[Dict[str, str]] = None,
                 filter: Optional[Dict[str, Any]] = None) -> str:
    """Get value maps from Zabbix.

    Args:
        valuemapids: List of value map IDs to retrieve
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of value maps
    """
    client = get_zabbix_client()
    params = {"output": "extend", "selectMappings": "extend"}

    if valuemapids:
        params["valuemapids"] = valuemapids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.valuemap.get(**params)
    return format_response(result)


@writable_tool()
def valuemap_create(name: str, mappings: List[Dict[str, str]], hostid: Optional[str] = None) -> str:
    """Create a new value map in Zabbix.

    Args:
        name: Value map name
        mappings: List of mappings, each with 'value' and 'newvalue'
        hostid: Host or template ID that the value map belongs to

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "mappings": mappings
    }

    if hostid is not None:
        params["hostid"] = hostid

    result = client.valuemap.create(**params)
    return format_response(result)


@writable_tool()
def valuemap_update(valuemapid: str, name: Optional[str] = None,
                    mappings: Optional[List[Dict[str, str]]] = None) -> str:
    """Update an existing value map in Zabbix.

    Args:
        valuemapid: Value map ID to update
        name: New value map name
        mappings: New mappings (replaces existing)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"valuemapid": valuemapid}

    if name:
        params["name"] = name
    if mappings:
        params["mappings"] = mappings

    result = client.valuemap.update(**params)
    return format_response(result)


@writable_tool()
def valuemap_delete(valuemapids: List[str]) -> str:
    """Delete value maps from Zabbix.

    Args:
        valuemapids: List of value map IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.valuemap.delete(*valuemapids)
    return format_response(result)
