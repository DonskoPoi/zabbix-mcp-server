"""
Event management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def event_get(eventids: Optional[List[str]] = None,
              groupids: Optional[List[str]] = None,
              hostids: Optional[List[str]] = None,
              objectids: Optional[List[str]] = None,
              output: Union[str, List[str]] = "extend",
              time_from: Optional[int] = None,
              time_till: Optional[int] = None,
              limit: Optional[int] = None) -> str:
    """Get events from Zabbix with optional filtering.

    Args:
        eventids: List of event IDs to retrieve
        groupids: List of host group IDs to filter by
        hostids: List of host IDs to filter by
        objectids: List of object IDs to filter by
        output: Output format (extend or list of specific fields)
        time_from: Start time (Unix timestamp)
        time_till: End time (Unix timestamp)
        limit: Maximum number of results

    Returns:
        str: JSON formatted list of events
    """
    client = get_zabbix_client()
    params = {"output": output}

    if eventids:
        params["eventids"] = eventids
    if groupids:
        params["groupids"] = groupids
    if hostids:
        params["hostids"] = hostids
    if objectids:
        params["objectids"] = objectids
    if time_from:
        params["time_from"] = time_from
    if time_till:
        params["time_till"] = time_till
    if limit:
        params["limit"] = limit

    result = client.event.get(**params)
    return format_response(result)


@writable_tool()
def event_acknowledge(eventids: List[str], action: int = 1,
                      message: Optional[str] = None) -> str:
    """Acknowledge events in Zabbix.

    Args:
        eventids: List of event IDs to acknowledge
        action: Acknowledge action (1=acknowledge, 2=close, etc.)
        message: Acknowledge message

    Returns:
        str: JSON formatted acknowledgment result
    """
    client = get_zabbix_client()
    params = {
        "eventids": eventids,
        "action": action
    }

    if message:
        params["message"] = message

    result = client.event.acknowledge(**params)
    return format_response(result)
