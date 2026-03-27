"""
Item management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def item_get(itemids: Optional[List[str]] = None,
             hostids: Optional[List[str]] = None,
             groupids: Optional[List[str]] = None,
             templateids: Optional[List[str]] = None,
             output: Union[str, List[str]] = "extend",
             search: Optional[Dict[str, str]] = None,
             filter: Optional[Dict[str, Any]] = None,
             limit: Optional[int] = None) -> str:
    """Get items from Zabbix with optional filtering.

    Args:
        itemids: List of item IDs to retrieve
        hostids: List of host IDs to filter by
        groupids: List of host group IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results

    Returns:
        str: JSON formatted list of items
    """
    client = get_zabbix_client()
    params = {"output": output}

    if itemids:
        params["itemids"] = itemids
    if hostids:
        params["hostids"] = hostids
    if groupids:
        params["groupids"] = groupids
    if templateids:
        params["templateids"] = templateids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    if limit:
        params["limit"] = limit

    result = client.item.get(**params)
    return format_response(result)


@writable_tool()
def item_create(name: str, key_: str, hostid: str, type: int,
                value_type: int, delay: str = "1m",
                interfaceid: Optional[str] = None,
                units: Optional[str] = None,
                description: Optional[str] = None) -> str:
    """Create a new item in Zabbix.

    Args:
        name: Item name
        key_: Item key
        hostid: Host ID
        type: Item type (0=Zabbix agent, 2=Zabbix trapper, etc.)
        value_type: Value type (0=float, 1=character, 3=unsigned int, 4=text)
        delay: Update interval
        interfaceid: Interface ID (required for Zabbix agent items)
        units: Value units
        description: Item description

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "key_": key_,
        "hostid": hostid,
        "type": type,
        "value_type": value_type,
        "delay": delay
    }

    if interfaceid:
        params["interfaceid"] = interfaceid
    if units:
        params["units"] = units
    if description:
        params["description"] = description

    result = client.item.create(**params)
    return format_response(result)


@writable_tool()
def item_update(itemid: str, name: Optional[str] = None,
                key_: Optional[str] = None, delay: Optional[str] = None,
                status: Optional[int] = None, valuemapid: Optional[str] = None) -> str:
    """Update an existing item in Zabbix.

    Args:
        itemid: Item ID to update
        name: New item name
        key_: New item key
        delay: New update interval
        status: New status (0=enabled, 1=disabled)
        valuemapid: Value map ID to apply to the item

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"itemid": itemid}

    if name:
        params["name"] = name
    if key_:
        params["key_"] = key_
    if delay:
        params["delay"] = delay
    if status is not None:
        params["status"] = status
    if valuemapid is not None:
        params["valuemapid"] = valuemapid

    result = client.item.update(**params)
    return format_response(result)


@writable_tool()
def item_delete(itemids: List[str]) -> str:
    """Delete items from Zabbix.

    Args:
        itemids: List of item IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.item.delete(*itemids)
    return format_response(result)
