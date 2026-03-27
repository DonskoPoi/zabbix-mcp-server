"""
Maintenance management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def maintenance_get(maintenanceids: Optional[List[str]] = None,
                    groupids: Optional[List[str]] = None,
                    hostids: Optional[List[str]] = None,
                    output: Union[str, List[str]] = "extend") -> str:
    """Get maintenance periods from Zabbix.

    Args:
        maintenanceids: List of maintenance IDs to retrieve
        groupids: List of host group IDs to filter by
        hostids: List of host IDs to filter by
        output: Output format (extend or list of specific fields)

    Returns:
        str: JSON formatted list of maintenance periods
    """
    client = get_zabbix_client()
    params = {"output": output}

    if maintenanceids:
        params["maintenanceids"] = maintenanceids
    if groupids:
        params["groupids"] = groupids
    if hostids:
        params["hostids"] = hostids

    result = client.maintenance.get(**params)
    return format_response(result)


@writable_tool()
def maintenance_create(name: str, active_since: int, active_till: int,
                       groupids: Optional[List[str]] = None,
                       hostids: Optional[List[str]] = None,
                       timeperiods: Optional[List[Dict[str, Any]]] = None,
                       description: Optional[str] = None) -> str:
    """Create a new maintenance period in Zabbix.

    Args:
        name: Maintenance name
        active_since: Start time (Unix timestamp)
        active_till: End time (Unix timestamp)
        groupids: List of host group IDs
        hostids: List of host IDs
        timeperiods: List of time periods
        description: Maintenance description

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "active_since": active_since,
        "active_till": active_till
    }

    if groupids:
        params["groupids"] = groupids
    if hostids:
        params["hostids"] = hostids
    if timeperiods:
        params["timeperiods"] = timeperiods
    if description:
        params["description"] = description

    result = client.maintenance.create(**params)
    return format_response(result)


@writable_tool()
def maintenance_update(maintenanceid: str, name: Optional[str] = None,
                       active_since: Optional[int] = None, active_till: Optional[int] = None,
                       description: Optional[str] = None) -> str:
    """Update an existing maintenance period in Zabbix.

    Args:
        maintenanceid: Maintenance ID to update
        name: New maintenance name
        active_since: New start time (Unix timestamp)
        active_till: New end time (Unix timestamp)
        description: New maintenance description

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"maintenanceid": maintenanceid}

    if name:
        params["name"] = name
    if active_since:
        params["active_since"] = active_since
    if active_till:
        params["active_till"] = active_till
    if description:
        params["description"] = description

    result = client.maintenance.update(**params)
    return format_response(result)


@writable_tool()
def maintenance_delete(maintenanceids: List[str]) -> str:
    """Delete maintenance periods from Zabbix.

    Args:
        maintenanceids: List of maintenance IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.maintenance.delete(*maintenanceids)
    return format_response(result)
