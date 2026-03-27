"""
Problem management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool


@readonly_tool()
def problem_get(eventids: Optional[List[str]] = None,
                groupids: Optional[List[str]] = None,
                hostids: Optional[List[str]] = None,
                objectids: Optional[List[str]] = None,
                output: Union[str, List[str]] = "extend",
                time_from: Optional[int] = None,
                time_till: Optional[int] = None,
                recent: bool = False,
                severities: Optional[List[int]] = None,
                limit: Optional[int] = None) -> str:
    """Get problems from Zabbix with optional filtering.

    Args:
        eventids: List of event IDs to retrieve
        groupids: List of host group IDs to filter by
        hostids: List of host IDs to filter by
        objectids: List of object IDs to filter by
        output: Output format (extend or list of specific fields)
        time_from: Start time (Unix timestamp)
        time_till: End time (Unix timestamp)
        recent: Only recent problems
        severities: List of severity levels to filter by
        limit: Maximum number of results

    Returns:
        str: JSON formatted list of problems
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
    if recent:
        params["recent"] = recent
    if severities:
        params["severities"] = severities
    if limit:
        params["limit"] = limit

    result = client.problem.get(**params)
    return format_response(result)
