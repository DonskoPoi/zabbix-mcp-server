"""
Graph management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def graph_get(graphids: Optional[List[str]] = None,
              hostids: Optional[List[str]] = None,
              templateids: Optional[List[str]] = None,
              output: Union[str, List[str]] = "extend",
              search: Optional[Dict[str, str]] = None,
              filter: Optional[Dict[str, Any]] = None) -> str:
    """Get graphs from Zabbix with optional filtering.

    Args:
        graphids: List of graph IDs to retrieve
        hostids: List of host IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of graphs
    """
    client = get_zabbix_client()
    params = {"output": output}

    if graphids:
        params["graphids"] = graphids
    if hostids:
        params["hostids"] = hostids
    if templateids:
        params["templateids"] = templateids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.graph.get(**params)
    return format_response(result)


@writable_tool()
def graph_create(name: str, hostid: Optional[str] = None,
                 templateid: Optional[str] = None,
                 width: int = 900, height: int = 200,
                 graphtype: int = 0,
                 show_legend: int = 1,
                 show_work_period: int = 1,
                 show_triggers: int = 1,
                 gitems: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a new graph in Zabbix.

    Args:
        name: Graph name
        hostid: Host ID (either hostid or templateid required)
        templateid: Template ID (either hostid or templateid required)
        width: Graph width in pixels
        height: Graph height in pixels
        graphtype: Graph type (0=normal, 1=stacked, 2=pie, 3=exploded)
        show_legend: Show legend (0=no, 1=yes)
        show_work_period: Show work period (0=no, 1=yes)
        show_triggers: Show triggers (0=no, 1=yes)
        gitems: Graph items list, each with itemid, color, drawtype, sortorder

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "width": width,
        "height": height,
        "graphtype": graphtype,
        "show_legend": show_legend,
        "show_work_period": show_work_period,
        "show_triggers": show_triggers
    }

    if hostid:
        params["hostid"] = hostid
    if templateid:
        params["templateid"] = templateid
    if gitems:
        params["gitems"] = gitems

    result = client.graph.create(**params)
    return format_response(result)


@writable_tool()
def graph_update(graphid: str, name: Optional[str] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 graphtype: Optional[int] = None,
                 show_legend: Optional[int] = None,
                 gitems: Optional[List[Dict[str, Any]]] = None) -> str:
    """Update an existing graph in Zabbix.

    Args:
        graphid: Graph ID to update
        name: New graph name
        width: New graph width
        height: New graph height
        graphtype: New graph type
        show_legend: New show legend setting
        gitems: New graph items (replaces existing)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"graphid": graphid}

    if name is not None:
        params["name"] = name
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height
    if graphtype is not None:
        params["graphtype"] = graphtype
    if show_legend is not None:
        params["show_legend"] = show_legend
    if gitems:
        params["gitems"] = gitems

    result = client.graph.update(**params)
    return format_response(result)


@writable_tool()
def graph_delete(graphids: List[str]) -> str:
    """Delete graphs from Zabbix.

    Args:
        graphids: List of graph IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.graph.delete(*graphids)
    return format_response(result)
