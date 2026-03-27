"""
Action management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def action_get(actionids: Optional[List[str]] = None,
               groupids: Optional[List[str]] = None,
               hostids: Optional[List[str]] = None,
               triggerids: Optional[List[str]] = None,
               usrgrpids: Optional[List[str]] = None,
               userids: Optional[List[str]] = None,
               scriptids: Optional[List[str]] = None,
               output: Union[str, List[str]] = "extend",
               selectFilter: Optional[Union[str, List[str]]] = None,
               selectOperations: Optional[Union[str, List[str]]] = None,
               selectRecoveryOperations: Optional[Union[str, List[str]]] = None,
               selectUpdateOperations: Optional[Union[str, List[str]]] = None,
               search: Optional[Dict[str, str]] = None,
               filter: Optional[Dict[str, Any]] = None) -> str:
    """Get actions from Zabbix with optional filtering.

    Args:
        actionids: List of action IDs to retrieve
        groupids: Filter by host group IDs
        hostids: Filter by host IDs
        triggerids: Filter by trigger IDs
        usrgrpids: Filter by user group IDs
        userids: Filter by user IDs
        scriptids: Filter by script IDs
        output: Output format (extend or list of specific fields)
        selectFilter: Return action filter
        selectOperations: Return action operations
        selectRecoveryOperations: Return action recovery operations
        selectUpdateOperations: Return action update operations
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of actions
    """
    client = get_zabbix_client()
    params = {"output": output}

    if actionids:
        params["actionids"] = actionids
    if groupids:
        params["groupids"] = groupids
    if hostids:
        params["hostids"] = hostids
    if triggerids:
        params["triggerids"] = triggerids
    if usrgrpids:
        params["usrgrpids"] = usrgrpids
    if userids:
        params["userids"] = userids
    if scriptids:
        params["scriptids"] = scriptids
    if selectFilter is not None:
        params["selectFilter"] = selectFilter
    if selectOperations is not None:
        params["selectOperations"] = selectOperations
    if selectRecoveryOperations is not None:
        params["selectRecoveryOperations"] = selectRecoveryOperations
    if selectUpdateOperations is not None:
        params["selectUpdateOperations"] = selectUpdateOperations
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.action.get(**params)
    return format_response(result)


@writable_tool()
def action_create(name: str,
                  eventsource: int,
                  status: Optional[int] = None,
                  esc_period: Optional[str] = None,
                  def_shortdata: Optional[str] = None,
                  def_longdata: Optional[str] = None,
                  r_shortdata: Optional[str] = None,
                  r_longdata: Optional[str] = None,
                  filter: Optional[Dict[str, Any]] = None,
                  operations: Optional[List[Dict[str, Any]]] = None,
                  recovery_operations: Optional[List[Dict[str, Any]]] = None,
                  update_operations: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a new action in Zabbix.

    Args:
        name: Action name
        eventsource: Event source (0=trigger, 1=discovery, 2=autoregistration, 3=internal)
        status: Status (0=enabled, 1=disabled)
        esc_period: Escalation period (e.g., "1h", "30m")
        def_shortdata: Default short data
        def_longdata: Default long data
        r_shortdata: Recovery short data
        r_longdata: Recovery long data
        filter: Action filter (evaltype, conditions, etc.)
        operations: Action operations
        recovery_operations: Recovery operations
        update_operations: Update operations

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "eventsource": eventsource
    }

    if status is not None:
        params["status"] = status
    if esc_period is not None:
        params["esc_period"] = esc_period
    if def_shortdata is not None:
        params["def_shortdata"] = def_shortdata
    if def_longdata is not None:
        params["def_longdata"] = def_longdata
    if r_shortdata is not None:
        params["r_shortdata"] = r_shortdata
    if r_longdata is not None:
        params["r_longdata"] = r_longdata
    if filter is not None:
        params["filter"] = filter
    if operations is not None:
        params["operations"] = operations
    if recovery_operations is not None:
        params["recovery_operations"] = recovery_operations
    if update_operations is not None:
        params["update_operations"] = update_operations

    result = client.action.create(**params)
    return format_response(result)


@writable_tool()
def action_update(actionid: str,
                  name: Optional[str] = None,
                  eventsource: Optional[int] = None,
                  status: Optional[int] = None,
                  esc_period: Optional[str] = None,
                  def_shortdata: Optional[str] = None,
                  def_longdata: Optional[str] = None,
                  r_shortdata: Optional[str] = None,
                  r_longdata: Optional[str] = None,
                  filter: Optional[Dict[str, Any]] = None,
                  operations: Optional[List[Dict[str, Any]]] = None,
                  recovery_operations: Optional[List[Dict[str, Any]]] = None,
                  update_operations: Optional[List[Dict[str, Any]]] = None) -> str:
    """Update an existing action in Zabbix.

    Args:
        actionid: Action ID to update
        name: New action name
        eventsource: New event source
        status: New status (0=enabled, 1=disabled)
        esc_period: New escalation period
        def_shortdata: New default short data
        def_longdata: New default long data
        r_shortdata: New recovery short data
        r_longdata: New recovery long data
        filter: New action filter
        operations: New action operations (replaces existing)
        recovery_operations: New recovery operations (replaces existing)
        update_operations: New update operations (replaces existing)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"actionid": actionid}

    if name is not None:
        params["name"] = name
    if eventsource is not None:
        params["eventsource"] = eventsource
    if status is not None:
        params["status"] = status
    if esc_period is not None:
        params["esc_period"] = esc_period
    if def_shortdata is not None:
        params["def_shortdata"] = def_shortdata
    if def_longdata is not None:
        params["def_longdata"] = def_longdata
    if r_shortdata is not None:
        params["r_shortdata"] = r_shortdata
    if r_longdata is not None:
        params["r_longdata"] = r_longdata
    if filter is not None:
        params["filter"] = filter
    if operations is not None:
        params["operations"] = operations
    if recovery_operations is not None:
        params["recovery_operations"] = recovery_operations
    if update_operations is not None:
        params["update_operations"] = update_operations

    result = client.action.update(**params)
    return format_response(result)


@writable_tool()
def action_delete(actionids: List[str]) -> str:
    """Delete actions from Zabbix.

    Args:
        actionids: List of action IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.action.delete(*actionids)
    return format_response(result)
