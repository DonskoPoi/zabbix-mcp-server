"""
Dashboard management tools (including auto dashboard) for Zabbix MCP Server.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool

logger = logging.getLogger(__name__)

# Dashboard widget type constants
WIDGET_TYPE_CLOCK = "clock"
WIDGET_TYPE_SYSTEM_INFO = "systeminfo"
WIDGET_TYPE_PROBLEMS = "problems"
WIDGET_TYPE_MAP = "map"
WIDGET_TYPE_HOST_CARD = "hostcard"
WIDGET_TYPE_GRAPH = "graph"
WIDGET_TYPE_TRIGGERS = "triggers"
WIDGET_TYPE_ITEM_VALUE = "itemvalue"

# Dashboard default dimensions
DASHBOARD_MAX_WIDTH = 72


def _build_widget(widget_type: str,
                  name: str,
                  x: int,
                  y: int,
                  width: int,
                  height: int,
                  view_mode: int = 0,
                  fields: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Build a standard widget structure.

    Args:
        widget_type: Widget type (clock, problems, map, etc.)
        name: Widget display name
        x: X position (0-based)
        y: Y position (0-based)
        width: Widget width (max 72)
        height: Widget height
        view_mode: View mode (0 = default)
        fields: List of widget field configurations

    Returns:
        Widget configuration dictionary
    """
    widget = {
        "type": widget_type,
        "name": name,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "view_mode": view_mode
    }
    if fields:
        widget["fields"] = fields
    return widget


def _find_dashboard_by_name(client, name: str) -> Optional[Dict[str, Any]]:
    """Find an existing dashboard by name.

    Args:
        client: Zabbix API client
        name: Dashboard name to search for

    Returns:
        Dashboard data if found, None otherwise
    """
    result = client.dashboard.get(
        filter={"name": name},
        output=["dashboardid", "name"]
    )
    return result[0] if result else None


def _find_map_by_name_or_id(client,
                            map_name: Optional[str] = None,
                            map_ids: Optional[List[str]] = None) -> Optional[str]:
    """Find a map by name or ID.

    Args:
        client: Zabbix API client
        map_name: Map name to search for
        map_ids: List of map IDs (priority over name)

    Returns:
        Map ID if found, None otherwise
    """
    if map_ids:
        result = client.map.get(
            sysmapids=map_ids,
            output=["sysmapid", "name"]
        )
        return result[0]["sysmapid"] if result else None

    if map_name:
        result = client.map.get(
            filter={"name": map_name},
            output=["sysmapid", "name"]
        )
        return result[0]["sysmapid"] if result else None

    return None


def _get_hosts_by_groups(client,
                         host_group_names: Optional[List[str]] = None,
                         host_group_ids: Optional[List[str]] = None,
                         limit: int = 4) -> List[Dict[str, Any]]:
    """Get hosts from specified host groups.

    Args:
        client: Zabbix API client
        host_group_names: List of host group names
        host_group_ids: List of host group IDs
        limit: Maximum number of hosts to return

    Returns:
        List of host data dictionaries
    """
    params = {
        "output": ["hostid", "name", "host"],
        "limit": limit,
        "sortfield": "name"
    }

    if host_group_ids:
        params["groupids"] = host_group_ids
    elif host_group_names:
        groups = client.hostgroup.get(
            filter={"name": host_group_names},
            output=["groupid"]
        )
        if groups:
            params["groupids"] = [g["groupid"] for g in groups]

    return client.host.get(**params)


def _build_system_overview_pages(client,
                                  map_id: Optional[str],
                                  host_group_ids: Optional[List[str]] = None,
                                  host_group_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Build pages structure for System Overview dashboard.

    Layout:
    y=0, height=3: System info + Clock + Problems
    y=3, height=10: Map (if available)
    y=13, height=8: Host cards

    Args:
        client: Zabbix API client
        map_id: Map ID to display
        host_group_ids: Host group IDs to use for host cards
        host_group_names: Host group names to use for host cards

    Returns:
        List of dashboard page configurations
    """
    widgets = []

    # Top row: System info, Clock, Problems
    widgets.append(_build_widget(
        WIDGET_TYPE_SYSTEM_INFO,
        "System Information",
        x=0, y=0, width=24, height=3
    ))

    widgets.append(_build_widget(
        WIDGET_TYPE_CLOCK,
        "Clock",
        x=24, y=0, width=24, height=3,
        fields=[
            {"type": 0, "name": "clock_type", "value": 1},
            {"type": 0, "name": "show.0", "value": 1},
            {"type": 0, "name": "show.1", "value": 2}
        ]
    ))

    widgets.append(_build_widget(
        WIDGET_TYPE_PROBLEMS,
        "Problems",
        x=48, y=0, width=24, height=3,
        fields=[
            {"type": 0, "name": "show_type", "value": 0},
            {"type": 0, "name": "show_lines", "value": 5},
            {"type": 0, "name": "hide_problem_events.0", "value": 0},
            {"type": 0, "name": "hide_problem_events.1", "value": 1}
        ]
    ))

    current_y = 3

    # Map widget (if map_id is provided)
    if map_id:
        widgets.append(_build_widget(
            WIDGET_TYPE_MAP,
            "Topology Map",
            x=0, y=current_y, width=72, height=10,
            fields=[
                {"type": 8, "name": "sysmapid", "value": map_id}
            ]
        ))
        current_y += 10

    # Host cards - get up to 4 hosts
    hosts = _get_hosts_by_groups(
        client,
        host_group_names=host_group_names,
        host_group_ids=host_group_ids,
        limit=4
    )

    host_card_width = 18
    for i, host in enumerate(hosts[:4]):
        widgets.append(_build_widget(
            WIDGET_TYPE_HOST_CARD,
            f"Host: {host['name']}",
            x=i * host_card_width,
            y=current_y,
            width=host_card_width,
            height=8,
            fields=[
                {"type": 8, "name": "hostid", "value": host["hostid"]}
            ]
        ))

    return [{"widgets": widgets}]


def _get_host_key_graphs(client, hostid: str) -> Dict[str, Optional[str]]:
    """Get key graphs for a host (CPU, memory, disk, network).

    Args:
        client: Zabbix API client
        hostid: Host ID

    Returns:
        Dictionary with graph IDs for each metric type
    """
    graphs = client.graph.get(
        hostids=[hostid],
        output=["graphid", "name"]
    )

    result = {
        "cpu": None,
        "memory": None,
        "disk": None,
        "network": None
    }

    # Try to find matching graphs by name patterns
    for graph in graphs:
        name_lower = graph["name"].lower()
        if not result["cpu"] and ("cpu" in name_lower or "processor" in name_lower):
            result["cpu"] = graph["graphid"]
        elif not result["memory"] and ("memory" in name_lower or "ram" in name_lower):
            result["memory"] = graph["graphid"]
        elif not result["disk"] and ("disk" in name_lower or "space" in name_lower or "filesystem" in name_lower):
            result["disk"] = graph["graphid"]
        elif not result["network"] and ("network" in name_lower or "interface" in name_lower or "traffic" in name_lower):
            result["network"] = graph["graphid"]

    return result


def _build_host_detail_pages(client,
                              hostid: str,
                              host_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build pages structure for Host Detail dashboard.

    Layout:
    y=0, height=5: Host card + Problems
    y=5, height=5: CPU, Memory, Disk, Network graphs
    y=10, height=6: Triggers

    Args:
        client: Zabbix API client
        hostid: Host ID
        host_data: Host data dictionary

    Returns:
        List of dashboard page configurations
    """
    widgets = []

    # Top row: Host card + Problems
    widgets.append(_build_widget(
        WIDGET_TYPE_HOST_CARD,
        f"Host: {host_data.get('name', hostid)}",
        x=0, y=0, width=36, height=5,
        fields=[
            {"type": 8, "name": "hostid", "value": hostid}
        ]
    ))

    widgets.append(_build_widget(
        WIDGET_TYPE_PROBLEMS,
        "Host Problems",
        x=36, y=0, width=36, height=5,
        fields=[
            {"type": 8, "name": "hostids.0", "value": hostid},
            {"type": 0, "name": "show_lines", "value": 10}
        ]
    ))

    # Graph row: CPU, Memory, Disk, Network
    graphs = _get_host_key_graphs(client, hostid)
    graph_types = [
        ("cpu", "CPU Usage"),
        ("memory", "Memory Usage"),
        ("disk", "Disk Space"),
        ("network", "Network Traffic")
    ]

    for i, (graph_key, graph_name) in enumerate(graph_types):
        graph_id = graphs.get(graph_key)
        fields = []
        if graph_id:
            fields = [{"type": 8, "name": "graphid", "value": graph_id}]

        widgets.append(_build_widget(
            WIDGET_TYPE_GRAPH,
            graph_name,
            x=i * 18, y=5, width=18, height=5,
            fields=fields
        ))

    # Bottom: Triggers
    widgets.append(_build_widget(
        WIDGET_TYPE_TRIGGERS,
        "Host Triggers",
        x=0, y=10, width=72, height=6,
        fields=[
            {"type": 8, "name": "hostids.0", "value": hostid},
            {"type": 0, "name": "show_lines", "value": 15},
            {"type": 0, "name": "sort_triggers", "value": 3}
        ]
    ))

    return [{"widgets": widgets}]


def _auto_dashboard_system_overview_core(dashboard_name: str,
                                          map_name: Optional[str] = None,
                                          map_ids: Optional[List[str]] = None,
                                          host_group_names: Optional[List[str]] = None,
                                          host_group_ids: Optional[List[str]] = None,
                                          create_if_missing: bool = True,
                                          update_if_exists: bool = False) -> Dict[str, Any]:
    """Core function for creating/updating System Overview dashboard.

    Args:
        dashboard_name: Dashboard name
        map_name: Map name to display
        map_ids: Map IDs to display (priority over map_name)
        host_group_names: Host group names for host cards
        host_group_ids: Host group IDs for host cards
        create_if_missing: Create if dashboard doesn't exist
        update_if_exists: Update if dashboard exists

    Returns:
        Result dictionary with action taken
    """
    client = get_zabbix_client()

    # Find or validate map
    map_id = _find_map_by_name_or_id(client, map_name=map_name, map_ids=map_ids)

    # Check if dashboard exists
    existing_dashboard = _find_dashboard_by_name(client, dashboard_name)

    # Build pages
    pages = _build_system_overview_pages(
        client,
        map_id=map_id,
        host_group_ids=host_group_ids,
        host_group_names=host_group_names
    )

    result = {
        "dashboard_name": dashboard_name,
        "map_id": map_id,
        "action": "none"
    }

    if existing_dashboard:
        if update_if_exists:
            # Update existing dashboard
            dashboardid = existing_dashboard["dashboardid"]
            client.dashboard.update(
                dashboardid=dashboardid,
                pages=pages
            )
            result["action"] = "updated"
            result["dashboardid"] = dashboardid
        else:
            result["action"] = "skipped"
            result["warning"] = "Dashboard already exists and update_if_exists is False"
            result["dashboardid"] = existing_dashboard["dashboardid"]
    elif create_if_missing:
        # Create new dashboard
        create_result = client.dashboard.create(
            name=dashboard_name,
            pages=pages
        )
        result["action"] = "created"
        result["dashboardid"] = create_result.get("dashboardids", [None])[0]
    else:
        result["action"] = "none"
        result["warning"] = "Dashboard does not exist and create_if_missing is False"

    return result


def _auto_dashboard_host_detail_core(hostid: str,
                                      dashboard_name: Optional[str] = None,
                                      create_if_missing: bool = True,
                                      update_if_exists: bool = False) -> Dict[str, Any]:
    """Core function for creating/updating Host Detail dashboard.

    Args:
        hostid: Host ID
        dashboard_name: Dashboard name (defaults to "Host Detail - {host name}")
        create_if_missing: Create if dashboard doesn't exist
        update_if_exists: Update if dashboard exists

    Returns:
        Result dictionary with action taken
    """
    client = get_zabbix_client()

    # Get host data
    hosts = client.host.get(
        hostids=[hostid],
        output=["hostid", "name", "host"]
    )
    if not hosts:
        raise ValueError(f"Host with ID {hostid} not found")

    host_data = hosts[0]

    # Determine dashboard name
    if not dashboard_name:
        dashboard_name = f"Host Detail - {host_data.get('name', hostid)}"

    # Check if dashboard exists
    existing_dashboard = _find_dashboard_by_name(client, dashboard_name)

    # Build pages
    pages = _build_host_detail_pages(client, hostid=hostid, host_data=host_data)

    result = {
        "dashboard_name": dashboard_name,
        "hostid": hostid,
        "host_name": host_data.get("name"),
        "action": "none"
    }

    if existing_dashboard:
        if update_if_exists:
            # Update existing dashboard
            dashboardid = existing_dashboard["dashboardid"]
            client.dashboard.update(
                dashboardid=dashboardid,
                pages=pages
            )
            result["action"] = "updated"
            result["dashboardid"] = dashboardid
        else:
            result["action"] = "skipped"
            result["warning"] = "Dashboard already exists and update_if_exists is False"
            result["dashboardid"] = existing_dashboard["dashboardid"]
    elif create_if_missing:
        # Create new dashboard
        create_result = client.dashboard.create(
            name=dashboard_name,
            pages=pages
        )
        result["action"] = "created"
        result["dashboardid"] = create_result.get("dashboardids", [None])[0]
    else:
        result["action"] = "none"
        result["warning"] = "Dashboard does not exist and create_if_missing is False"

    return result


@readonly_tool()
def dashboard_get(dashboardids: Optional[List[str]] = None,
                  output: Union[str, List[str]] = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None,
                  limit: Optional[int] = None,
                  selectUsers: Optional[Union[str, List[str]]] = None,
                  selectUserGroups: Optional[Union[str, List[str]]] = None,
                  selectPages: Optional[Union[str, List[str]]] = None) -> str:
    """Get dashboards from Zabbix with optional filtering.

    Args:
        dashboardids: List of dashboard IDs to retrieve
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results
        selectUsers: Return users with access to dashboard
        selectUserGroups: Return user groups with access to dashboard
        selectPages: Return dashboard pages with widgets

    Returns:
        str: JSON formatted list of dashboards
    """
    client = get_zabbix_client()
    params = {"output": output}

    if dashboardids:
        params["dashboardids"] = dashboardids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    if limit:
        params["limit"] = limit
    if selectUsers is not None:
        params["selectUsers"] = selectUsers
    if selectUserGroups is not None:
        params["selectUserGroups"] = selectUserGroups
    if selectPages is not None:
        params["selectPages"] = selectPages

    result = client.dashboard.get(**params)
    return format_response(result)


@writable_tool()
def dashboard_create(name: str,
                     display_period: Optional[int] = None,
                     auto_start: Optional[int] = None,
                     pages: Optional[List[Dict[str, Any]]] = None,
                     users: Optional[List[Dict[str, Any]]] = None,
                     userGroups: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a new dashboard in Zabbix.

    Args:
        name: Dashboard name
        display_period: Page auto-switch period in seconds
        auto_start: Whether to auto-start slideshow (0 or 1)
        pages: Dashboard pages configuration with widgets
        users: User sharing configuration
        userGroups: User group sharing configuration

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {"name": name}

    if display_period is not None:
        params["display_period"] = display_period
    if auto_start is not None:
        params["auto_start"] = auto_start
    if pages:
        params["pages"] = pages
    if users:
        params["users"] = users
    if userGroups:
        params["userGroups"] = userGroups

    result = client.dashboard.create(**params)
    return format_response(result)


@writable_tool()
def dashboard_update(dashboardid: str,
                     name: Optional[str] = None,
                     display_period: Optional[int] = None,
                     auto_start: Optional[int] = None,
                     pages: Optional[List[Dict[str, Any]]] = None,
                     users: Optional[List[Dict[str, Any]]] = None,
                     userGroups: Optional[List[Dict[str, Any]]] = None) -> str:
    """Update an existing dashboard in Zabbix.

    Args:
        dashboardid: Dashboard ID to update
        name: New dashboard name
        display_period: New page auto-switch period in seconds
        auto_start: New auto-start slideshow setting (0 or 1)
        pages: New dashboard pages configuration with widgets
        users: New user sharing configuration (replaces existing)
        userGroups: New user group sharing configuration (replaces existing)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"dashboardid": dashboardid}

    if name is not None:
        params["name"] = name
    if display_period is not None:
        params["display_period"] = display_period
    if auto_start is not None:
        params["auto_start"] = auto_start
    if pages:
        params["pages"] = pages
    if users:
        params["users"] = users
    if userGroups:
        params["userGroups"] = userGroups

    result = client.dashboard.update(**params)
    return format_response(result)


@writable_tool()
def dashboard_delete(dashboardids: List[str]) -> str:
    """Delete dashboards from Zabbix.

    Args:
        dashboardids: List of dashboard IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.dashboard.delete(*dashboardids)
    return format_response(result)


@writable_tool()
def dashboard_create_system_overview(dashboard_name: str = "System Overview",
                                      map_name: Optional[str] = None,
                                      map_ids: Optional[List[str]] = None,
                                      host_group_names: Optional[List[str]] = None,
                                      host_group_ids: Optional[List[str]] = None,
                                      create_if_missing: bool = True,
                                      update_if_exists: bool = False) -> str:
    """Create a System Overview dashboard with preset widgets.

    Layout includes:
    - Top: System info + Clock + Problems overview
    - Middle: Topology map (if specified)
    - Bottom: Host cards for key hosts

    Args:
        dashboard_name: Dashboard name (default: "System Overview")
        map_name: Name of map to display in the dashboard
        map_ids: List of map IDs to display (priority over map_name)
        host_group_names: List of host group names to use for host cards
        host_group_ids: List of host group IDs to use for host cards
        create_if_missing: Create dashboard if it doesn't exist (default: True)
        update_if_exists: Update dashboard if it exists (default: False)

    Returns:
        JSON string with creation/update result
    """
    try:
        result = _auto_dashboard_system_overview_core(
            dashboard_name=dashboard_name,
            map_name=map_name,
            map_ids=map_ids,
            host_group_names=host_group_names,
            host_group_ids=host_group_ids,
            create_if_missing=create_if_missing,
            update_if_exists=update_if_exists
        )
        return format_response(result)
    except Exception as e:
        logger.error(f"Error in dashboard_create_system_overview: {e}")
        return format_response({"error": str(e)})


@writable_tool()
def dashboard_create_host_detail(hostid: str,
                                  dashboard_name: Optional[str] = None,
                                  create_if_missing: bool = True,
                                  update_if_exists: bool = False) -> str:
    """Create a Host Detail dashboard for a specific host with preset widgets.

    Layout includes:
    - Top: Host card + Host-specific problems
    - Middle: CPU, Memory, Disk, Network graphs
    - Bottom: Host triggers

    Args:
        hostid: Host ID (required)
        dashboard_name: Dashboard name (default: "Host Detail - {host name}")
        create_if_missing: Create dashboard if it doesn't exist (default: True)
        update_if_exists: Update dashboard if it exists (default: False)

    Returns:
        JSON string with creation/update result
    """
    try:
        result = _auto_dashboard_host_detail_core(
            hostid=hostid,
            dashboard_name=dashboard_name,
            create_if_missing=create_if_missing,
            update_if_exists=update_if_exists
        )
        return format_response(result)
    except Exception as e:
        logger.error(f"Error in dashboard_create_host_detail: {e}")
        return format_response({"error": str(e)})
