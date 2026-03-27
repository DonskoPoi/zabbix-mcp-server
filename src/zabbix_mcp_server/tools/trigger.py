"""
Trigger management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def trigger_get(triggerids: Optional[List[str]] = None,
                hostids: Optional[List[str]] = None,
                groupids: Optional[List[str]] = None,
                templateids: Optional[List[str]] = None,
                output: Union[str, List[str]] = "extend",
                search: Optional[Dict[str, str]] = None,
                filter: Optional[Dict[str, Any]] = None,
                limit: Optional[int] = None) -> str:
    """Get triggers from Zabbix with optional filtering.

    Args:
        triggerids: List of trigger IDs to retrieve
        hostids: List of host IDs to filter by
        groupids: List of host group IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results

    Returns:
        str: JSON formatted list of triggers
    """
    client = get_zabbix_client()
    params = {"output": output}

    if triggerids:
        params["triggerids"] = triggerids
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

    result = client.trigger.get(**params)
    return format_response(result)


@writable_tool()
def trigger_create(description: str, expression: str,
                   priority: int = 0, status: int = 0,
                   comments: Optional[str] = None) -> str:
    """Create a new trigger in Zabbix.

    Args:
        description: Trigger description
        expression: Trigger expression
        priority: Severity (0=not classified, 1=info, 2=warning, 3=average, 4=high, 5=disaster)
        status: Status (0=enabled, 1=disabled)
        comments: Additional comments

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "description": description,
        "expression": expression,
        "priority": priority,
        "status": status
    }

    if comments:
        params["comments"] = comments

    result = client.trigger.create(**params)
    return format_response(result)


@writable_tool()
def trigger_update(triggerid: str, description: Optional[str] = None,
                   expression: Optional[str] = None, priority: Optional[int] = None,
                   status: Optional[int] = None) -> str:
    """Update an existing trigger in Zabbix.

    Args:
        triggerid: Trigger ID to update
        description: New trigger description
        expression: New trigger expression
        priority: New severity level
        status: New status (0=enabled, 1=disabled)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"triggerid": triggerid}

    if description:
        params["description"] = description
    if expression:
        params["expression"] = expression
    if priority is not None:
        params["priority"] = priority
    if status is not None:
        params["status"] = status

    result = client.trigger.update(**params)
    return format_response(result)


@writable_tool()
def trigger_delete(triggerids: List[str]) -> str:
    """Delete triggers from Zabbix.

    Args:
        triggerids: List of trigger IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.trigger.delete(*triggerids)
    return format_response(result)
