"""
Map management tools (including auto map) for Zabbix MCP Server.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool

logger = logging.getLogger(__name__)

# Default icon configuration (built-in, no external file needed)
DEFAULT_ICON_CONFIG = {
    "default_host_type": "switch",
    "host_type": {
        "server": {
            "label": "{HOSTNAME}\n({HOST.IP})",
            "iconid_off": "150",
            "iconid_on": "150"
        },
        "switch": {
            "label": "{HOSTNAME}\n({HOST.IP})",
            "iconid_off": "154",
            "iconid_on": "154"
        },
        "router": {
            "label": "{HOSTNAME}\n({HOST.IP})",
            "iconid_off": "125",
            "iconid_on": "125"
        }
    }
}

# Check if igraph is available
try:
    import igraph
    HAS_IGRAPH = True
except ImportError:
    HAS_IGRAPH = False


def _parse_host_tags(host: Dict[str, Any], tag_prefix: str = "am.") -> Dict[str, Any]:
    """Parse host tags for automap configuration.

    Args:
        host: Host data from Zabbix API
        tag_prefix: Tag prefix to look for

    Returns:
        Dict with parsed configuration: host_type, label, links, etc.
    """
    result = {
        "host_type": None,
        "label": None,
        "links": []
    }

    tags = host.get("tags", [])
    for tag in tags:
        tag_key = tag.get("tag", "")
        tag_value = tag.get("value", "")

        if tag_key == f"{tag_prefix}host.type":
            result["host_type"] = tag_value
        elif tag_key == f"{tag_prefix}host.label":
            result["label"] = tag_value.replace("\\n", "\n")
        elif tag_key == f"{tag_prefix}link.connect_to":
            link = {
                "connect_to": tag_value,
                "label": None,
                "color": "00CC00",
                "draw_type": 0
            }
            result["links"].append(link)
        elif tag_key == f"{tag_prefix}link.label":
            if result["links"]:
                result["links"][-1]["label"] = tag_value
        elif tag_key == f"{tag_prefix}link.color":
            if result["links"]:
                result["links"][-1]["color"] = tag_value
        elif tag_key == f"{tag_prefix}link.draw_type":
            if result["links"]:
                try:
                    result["links"][-1]["draw_type"] = int(tag_value)
                except ValueError:
                    pass

    return result


def _compute_layout_grid(host_names: List[str], width: int, height: int, border: int = 100) -> Dict[str, Tuple[int, int]]:
    """Compute simple grid layout without external dependencies.

    Args:
        host_names: List of host names to position
        width: Map width
        height: Map height
        border: Border size

    Returns:
        Dict mapping host name to (x, y) coordinates
    """
    positions = {}
    n = len(host_names)

    if n == 0:
        return positions

    # Calculate grid dimensions
    cols = max(1, int(n ** 0.5))
    rows = (n + cols - 1) // cols

    # Calculate spacing
    usable_width = width - 2 * border
    usable_height = height - 2 * border

    spacing_x = usable_width // max(1, cols)
    spacing_y = usable_height // max(1, rows)

    for i, host_name in enumerate(host_names):
        row = i // cols
        col = i % cols
        x = border + col * spacing_x + spacing_x // 2
        y = border + row * spacing_y + spacing_y // 2
        positions[host_name] = (x, y)

    return positions


def _compute_layout_igraph(host_names: List[str], edges: List[Tuple[str, str]],
                           layout_type: str, width: int, height: int, border: int = 100) -> Dict[str, Tuple[int, int]]:
    """Compute layout using igraph.

    Args:
        host_names: List of host names
        edges: List of (host1, host2) tuples
        layout_type: Layout algorithm name
        width: Map width
        height: Map height
        border: Border size

    Returns:
        Dict mapping host name to (x, y) coordinates
    """
    if not HAS_IGRAPH:
        return _compute_layout_grid(host_names, width, height, border)

    g = igraph.Graph(directed=False)
    g.add_vertices(host_names)

    # Add edges (need to use vertex indices)
    name_to_idx = {name: i for i, name in enumerate(host_names)}
    edge_indices = []
    for h1, h2 in edges:
        if h1 in name_to_idx and h2 in name_to_idx:
            edge_indices.append((name_to_idx[h1], name_to_idx[h2]))

    if edge_indices:
        g.add_edges(edge_indices)

    # Compute layout
    try:
        layout = g.layout(layout_type)
    except ValueError:
        # Fallback to circle if layout type not supported
        layout = g.layout("circle")

    # Fit into bounding box
    bbox = (width - 2 * border, height - 2 * border)
    layout.fit_into(bbox=bbox)

    # Build position dict
    positions = {}
    for i, name in enumerate(host_names):
        x = int(layout.coords[i][0]) + border
        y = int(layout.coords[i][1]) + border
        positions[name] = (x, y)

    return positions


def _auto_map_core(map_name: str,
                   host_group_names: Optional[List[str]] = None,
                   host_group_ids: Optional[List[str]] = None,
                   tag_prefix: str = "am.",
                   layout: str = "grid",
                   width: int = 1920,
                   height: int = 1080,
                   force_relayout: bool = False,
                   create_if_missing: bool = True,
                   icon_config: Optional[Dict[str, Any]] = None,
                   preview_only: bool = False) -> Dict[str, Any]:
    """Core auto-map logic (shared between preview and update).

    Args:
        map_name: Map name
        host_group_names: Host group names to include
        host_group_ids: Host group IDs to include
        tag_prefix: Tag prefix for automap tags
        layout: Layout algorithm
        width: Map width for new maps
        height: Map height for new maps
        force_relayout: Force recompute all positions
        create_if_missing: Create map if it doesn't exist
        icon_config: Icon configuration
        preview_only: Only preview, don't modify

    Returns:
        Dict with result data
    """
    client = get_zabbix_client()

    if icon_config is None:
        icon_config = DEFAULT_ICON_CONFIG

    # Step 1: Get host groups
    groupids = []
    if host_group_ids:
        groupids.extend(host_group_ids)

    if host_group_names:
        for group_name in host_group_names:
            groups = client.hostgroup.get(
                output=["groupid"],
                filter={"name": [group_name]}
            )
            if groups:
                groupids.append(groups[0]["groupid"])

    # Step 2: Get hosts with tags
    host_params = {
        "output": ["hostid", "host", "name"],
        "selectTags": "extend"
    }
    if groupids:
        host_params["groupids"] = groupids

    hosts = client.host.get(**host_params)

    # Step 3: Parse tags and build host data
    host_data_by_name = {}
    host_data_by_id = {}
    edges = []
    all_link_targets = set()

    for host in hosts:
        host_name = host["host"]
        hostid = host["hostid"]
        parsed = _parse_host_tags(host, tag_prefix)

        # Determine host type and icon
        host_type = parsed["host_type"] or icon_config["default_host_type"]
        type_config = icon_config.get("host_type", {}).get(host_type, {})

        # Build label
        label = parsed["label"] or type_config.get("label", "{HOSTNAME}")
        label = label.replace("{HOSTNAME}", host_name)
        label = label.replace("{HOST.NAME}", host.get("name", host_name))

        host_data = {
            "hostid": hostid,
            "host": host_name,
            "name": host.get("name", host_name),
            "host_type": host_type,
            "label": label,
            "iconid_off": type_config.get("iconid_off", "154"),
            "iconid_on": type_config.get("iconid_on", "154"),
            "links": parsed["links"]
        }

        host_data_by_name[host_name] = host_data
        host_data_by_id[hostid] = host_data

        # Collect edges
        for link in parsed["links"]:
            connect_to = link["connect_to"]
            edges.append((host_name, connect_to, link))
            all_link_targets.add(connect_to)

    # Step 4: Check existing map
    existing_map = None
    existing_selements = []
    existing_links = []
    existing_positions = {}
    selementid_by_hostid = {}

    maps = client.map.get(
        output="extend",
        selectSelements="extend",
        selectLinks="extend",
        selectShapes="extend",
        selectLines="extend",
        filter={"name": [map_name]}
    )

    if maps:
        existing_map = maps[0]
        existing_selements = existing_map.get("selements", [])
        existing_links = existing_map.get("links", [])
        width = int(existing_map.get("width", width))
        height = int(existing_map.get("height", height))

        # Extract existing host positions
        for sel in existing_selements:
            elementtype = int(sel.get("elementtype", 0))
            if elementtype == 0 and sel.get("elements"):
                hostid = str(sel["elements"][0]["hostid"])
                existing_positions[hostid] = (int(sel["x"]), int(sel["y"]))
                selementid_by_hostid[hostid] = sel["selementid"]

    # Step 5: Compute positions
    host_names = list(host_data_by_name.keys())

    # Build edge list for layout
    layout_edges = []
    for h1, h2, _ in edges:
        if h1 in host_data_by_name and h2 in host_data_by_name:
            layout_edges.append((h1, h2))

    if force_relayout or not existing_positions:
        # Compute new layout
        if HAS_IGRAPH and layout != "grid":
            positions = _compute_layout_igraph(host_names, layout_edges, layout, width, height)
        else:
            positions = _compute_layout_grid(host_names, width, height)
    else:
        # Use existing positions where possible
        positions = {}
        needs_layout = []

        for host_name in host_names:
            hostid = host_data_by_name[host_name]["hostid"]
            if hostid in existing_positions:
                positions[host_name] = existing_positions[hostid]
            else:
                needs_layout.append(host_name)

        # Compute layout for new hosts
        if needs_layout:
            if HAS_IGRAPH and layout != "grid":
                new_positions = _compute_layout_igraph(needs_layout, [], layout, width, height)
            else:
                new_positions = _compute_layout_grid(needs_layout, width, height)
            positions.update(new_positions)

    # Step 6: Build selements
    new_selements = []
    non_host_selements = []
    preserved_host_selements = []

    # Separate non-host elements from existing
    for sel in existing_selements:
        elementtype = int(sel.get("elementtype", 0))
        if elementtype == 0 and sel.get("elements"):
            hostid = str(sel["elements"][0]["hostid"])
            if hostid not in host_data_by_id:
                # Preserve host elements not in our group
                preserved_host_selements.append(sel)
        else:
            # Preserve non-host elements (images, maps, etc.)
            non_host_selements.append(sel)

    # Build new host selements
    for host_name in host_names:
        host_data = host_data_by_name[host_name]
        hostid = host_data["hostid"]
        x, y = positions.get(host_name, (width // 2, height // 2))

        selement = {
            "elements": [{"hostid": hostid}],
            "elementtype": 0,
            "iconid_off": host_data["iconid_off"],
            "iconid_on": host_data["iconid_on"],
            "label": host_data["label"],
            "x": x,
            "y": y
        }

        if hostid in selementid_by_hostid:
            selement["selementid"] = selementid_by_hostid[hostid]
            if not force_relayout and hostid in existing_positions:
                selement["x"], selement["y"] = existing_positions[hostid]
        else:
            selement["selementid"] = f"tmp_{hostid}"

        new_selements.append(selement)

    # Step 7: Build links
    new_links = []
    preserved_non_host_links = []
    preserved_host_links = []

    # Index existing links
    def pair_key(a: str, b: str) -> tuple:
        return (a, b) if a <= b else (b, a)

    existing_host_links_by_pair = {}
    current_host_sids = set(selementid_by_hostid.values())

    for link in existing_links:
        sid1 = link.get("selementid1", "")
        sid2 = link.get("selementid2", "")
        if sid1 in current_host_sids and sid2 in current_host_sids:
            key = pair_key(sid1, sid2)
            if key not in existing_host_links_by_pair:
                existing_host_links_by_pair[key] = []
            existing_host_links_by_pair[key].append(link)
        else:
            preserved_non_host_links.append(link)

    # Build selementid lookup for new selements
    sid_by_hostid = {}
    for sel in new_selements:
        if sel.get("elements"):
            sid_by_hostid[sel["elements"][0]["hostid"]] = sel["selementid"]

    # Build new links from parsed data
    for host_name, target_name, link_data in edges:
        if host_name not in host_data_by_name or target_name not in host_data_by_name:
            continue

        hostid1 = host_data_by_name[host_name]["hostid"]
        hostid2 = host_data_by_name[target_name]["hostid"]
        sid1 = sid_by_hostid.get(hostid1)
        sid2 = sid_by_hostid.get(hostid2)

        if not sid1 or not sid2:
            continue

        key = pair_key(sid1, sid2)
        candidates = existing_host_links_by_pair.get(key, [])

        link_obj = {
            "selementid1": sid1,
            "selementid2": sid2,
            "label": link_data["label"] or "",
            "color": link_data["color"],
            "drawtype": link_data["draw_type"]
        }

        # Try to reuse existing link
        match_idx = None
        for idx, lnk in enumerate(candidates):
            if (lnk.get("label", "") == link_data["label"] and
                str(lnk.get("color", "")) == str(link_data["color"]) and
                int(lnk.get("drawtype", 0)) == int(link_data["draw_type"])):
                match_idx = idx
                break

        if match_idx is not None:
            lnk = candidates.pop(match_idx)
            link_obj["linkid"] = lnk["linkid"]
            if lnk.get("linktriggers"):
                link_obj["linktriggers"] = lnk["linktriggers"]
        elif candidates:
            lnk = candidates.pop(0)
            link_obj["linkid"] = lnk["linkid"]
            if lnk.get("linktriggers"):
                link_obj["linktriggers"] = lnk["linktriggers"]

        new_links.append(link_obj)

    # Preserve leftover existing host links
    for remaining in existing_host_links_by_pair.values():
        preserved_host_links.extend(remaining)

    # Step 8: Merge everything
    final_selements = non_host_selements + preserved_host_selements + new_selements
    final_links = preserved_non_host_links + new_links + preserved_host_links

    # Prepare result
    result = {
        "preview": {
            "map_name": map_name,
            "map_exists": existing_map is not None,
            "map_width": width,
            "map_height": height,
            "hosts_found": len(hosts),
            "hosts_in_map": len(host_names),
            "links_found": len(edges),
            "links_in_map": len(new_links),
            "host_details": [
                {
                    "host": h["host"],
                    "hostid": h["hostid"],
                    "host_type": h["host_type"],
                    "label": h["label"],
                    "position": positions.get(h["host"], (0, 0))
                }
                for h in host_data_by_name.values()
            ],
            "link_details": [
                {
                    "from": h1,
                    "to": h2,
                    "label": l.get("label"),
                    "color": l.get("color"),
                    "draw_type": l.get("draw_type")
                }
                for h1, h2, l in edges
                if h1 in host_data_by_name and h2 in host_data_by_name
            ]
        },
        "selements": final_selements,
        "links": final_links,
        "shapes": existing_map.get("shapes", []) if existing_map else [],
        "lines": existing_map.get("lines", []) if existing_map else []
    }

    # Perform update if not preview only
    if not preview_only:
        if existing_map:
            # Update existing map
            client.map.update(
                sysmapid=existing_map["sysmapid"],
                selements=final_selements,
                links=final_links
            )
            result["action"] = "updated"
            result["sysmapid"] = existing_map["sysmapid"]
        elif create_if_missing:
            # Create new map
            create_result = client.map.create(
                name=map_name,
                width=width,
                height=height,
                selements=final_selements,
                links=final_links
            )
            result["action"] = "created"
            result["sysmapid"] = create_result["sysmapids"][0] if create_result.get("sysmapids") else None
        else:
            result["action"] = "none"
            result["warning"] = "Map does not exist and create_if_missing is False"

    return result


@readonly_tool()
def map_get(sysmapids: Optional[List[str]] = None,
            output: Union[str, List[str]] = "extend",
            search: Optional[Dict[str, str]] = None,
            filter: Optional[Dict[str, Any]] = None,
            limit: Optional[int] = None,
            selectSelements: Optional[Union[str, List[str]]] = None,
            selectLinks: Optional[Union[str, List[str]]] = None,
            selectShapes: Optional[Union[str, List[str]]] = None,
            selectLines: Optional[Union[str, List[str]]] = None,
            selectUsers: Optional[Union[str, List[str]]] = None,
            selectUserGroups: Optional[Union[str, List[str]]] = None) -> str:
    """Get maps from Zabbix with optional filtering.

    Args:
        sysmapids: List of map IDs to retrieve
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results
        selectSelements: Return map elements (hosts, images, etc.)
        selectLinks: Return map links
        selectShapes: Return map shapes
        selectLines: Return map lines
        selectUsers: Return users with access to map
        selectUserGroups: Return user groups with access to map

    Returns:
        str: JSON formatted list of maps
    """
    client = get_zabbix_client()
    params = {"output": output}

    if sysmapids:
        params["sysmapids"] = sysmapids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    if limit:
        params["limit"] = limit
    if selectSelements is not None:
        params["selectSelements"] = selectSelements
    if selectLinks is not None:
        params["selectLinks"] = selectLinks
    if selectShapes is not None:
        params["selectShapes"] = selectShapes
    if selectLines is not None:
        params["selectLines"] = selectLines
    if selectUsers is not None:
        params["selectUsers"] = selectUsers
    if selectUserGroups is not None:
        params["selectUserGroups"] = selectUserGroups

    result = client.map.get(**params)
    return format_response(result)


@writable_tool()
def map_create(name: str, width: int, height: int,
               label_type: Optional[int] = None,
               label_location: Optional[int] = None,
               highlight: Optional[int] = None,
               expandproblem: Optional[int] = None,
               markelements: Optional[int] = None,
               show_unack: Optional[int] = None,
               grid_size: Optional[int] = None,
               grid_show: Optional[int] = None,
               grid_align: Optional[int] = None,
               backgroundid: Optional[str] = None,
               iconmapid: Optional[str] = None,
               expand_macros: Optional[int] = None,
               severity_min: Optional[int] = None,
               private: Optional[int] = None,
               show_suppressed: Optional[int] = None,
               selements: Optional[List[Dict[str, Any]]] = None,
               links: Optional[List[Dict[str, Any]]] = None,
               shapes: Optional[List[Dict[str, Any]]] = None,
               lines: Optional[List[Dict[str, Any]]] = None,
               users: Optional[List[Dict[str, Any]]] = None,
               userGroups: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a new map in Zabbix.

    Args:
        name: Map name
        width: Map width in pixels
        height: Map height in pixels
        label_type: Map element label type (0 - label, 1 - IP address, 2 - element name, 3 - status only)
        label_location: Map element label location (0 - bottom, 1 - left, 2 - right, 3 - top)
        highlight: Highlight map elements (0 - do not highlight, 1 - highlight)
        expandproblem: Expand problems (0 - do not expand, 1 - expand)
        markelements: Mark elements (0 - do not mark, 1 - mark)
        show_unack: Show unacknowledged problems (0 - do not show, 1 - show)
        grid_size: Grid size in pixels
        grid_show: Show grid (0 - do not show, 1 - show)
        grid_align: Align elements to grid (0 - do not align, 1 - align)
        backgroundid: Background image ID
        iconmapid: Icon map ID
        expand_macros: Expand macros in labels (0 - do not expand, 1 - expand)
        severity_min: Minimum problem severity to show (0-5)
        private: Map is private (0 - public, 1 - private)
        show_suppressed: Show suppressed problems (0 - do not show, 1 - show)
        selements: Map elements (hosts, images, etc.)
        links: Map links between elements
        shapes: Map shapes (rectangles, etc.)
        lines: Map lines
        users: Users with access to map
        userGroups: User groups with access to map

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "width": width,
        "height": height
    }

    if label_type is not None:
        params["label_type"] = label_type
    if label_location is not None:
        params["label_location"] = label_location
    if highlight is not None:
        params["highlight"] = highlight
    if expandproblem is not None:
        params["expandproblem"] = expandproblem
    if markelements is not None:
        params["markelements"] = markelements
    if show_unack is not None:
        params["show_unack"] = show_unack
    if grid_size is not None:
        params["grid_size"] = grid_size
    if grid_show is not None:
        params["grid_show"] = grid_show
    if grid_align is not None:
        params["grid_align"] = grid_align
    if backgroundid is not None:
        params["backgroundid"] = backgroundid
    if iconmapid is not None:
        params["iconmapid"] = iconmapid
    if expand_macros is not None:
        params["expand_macros"] = expand_macros
    if severity_min is not None:
        params["severity_min"] = severity_min
    if private is not None:
        params["private"] = private
    if show_suppressed is not None:
        params["show_suppressed"] = show_suppressed
    if selements:
        params["selements"] = selements
    if links:
        params["links"] = links
    if shapes:
        params["shapes"] = shapes
    if lines:
        params["lines"] = lines
    if users:
        params["users"] = users
    if userGroups:
        params["userGroups"] = userGroups

    result = client.map.create(**params)
    return format_response(result)


@writable_tool()
def map_update(sysmapid: str, name: Optional[str] = None,
               width: Optional[int] = None,
               height: Optional[int] = None,
               label_type: Optional[int] = None,
               label_location: Optional[int] = None,
               highlight: Optional[int] = None,
               expandproblem: Optional[int] = None,
               markelements: Optional[int] = None,
               show_unack: Optional[int] = None,
               grid_size: Optional[int] = None,
               grid_show: Optional[int] = None,
               grid_align: Optional[int] = None,
               backgroundid: Optional[str] = None,
               iconmapid: Optional[str] = None,
               expand_macros: Optional[int] = None,
               severity_min: Optional[int] = None,
               private: Optional[int] = None,
               show_suppressed: Optional[int] = None,
               selements: Optional[List[Dict[str, Any]]] = None,
               links: Optional[List[Dict[str, Any]]] = None,
               shapes: Optional[List[Dict[str, Any]]] = None,
               lines: Optional[List[Dict[str, Any]]] = None,
               users: Optional[List[Dict[str, Any]]] = None,
               userGroups: Optional[List[Dict[str, Any]]] = None) -> str:
    """Update an existing map in Zabbix.

    Args:
        sysmapid: Map ID to update
        name: New map name
        width: New map width in pixels
        height: New map height in pixels
        label_type: Map element label type
        label_location: Map element label location
        highlight: Highlight map elements
        expandproblem: Expand problems
        markelements: Mark elements
        show_unack: Show unacknowledged problems
        grid_size: Grid size in pixels
        grid_show: Show grid
        grid_align: Align elements to grid
        backgroundid: Background image ID
        iconmapid: Icon map ID
        expand_macros: Expand macros in labels
        severity_min: Minimum problem severity to show
        private: Map is private
        show_suppressed: Show suppressed problems
        selements: Map elements (replaces existing)
        links: Map links (replaces existing)
        shapes: Map shapes (replaces existing)
        lines: Map lines (replaces existing)
        users: Users with access to map (replaces existing)
        userGroups: User groups with access to map (replaces existing)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"sysmapid": sysmapid}

    if name is not None:
        params["name"] = name
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height
    if label_type is not None:
        params["label_type"] = label_type
    if label_location is not None:
        params["label_location"] = label_location
    if highlight is not None:
        params["highlight"] = highlight
    if expandproblem is not None:
        params["expandproblem"] = expandproblem
    if markelements is not None:
        params["markelements"] = markelements
    if show_unack is not None:
        params["show_unack"] = show_unack
    if grid_size is not None:
        params["grid_size"] = grid_size
    if grid_show is not None:
        params["grid_show"] = grid_show
    if grid_align is not None:
        params["grid_align"] = grid_align
    if backgroundid is not None:
        params["backgroundid"] = backgroundid
    if iconmapid is not None:
        params["iconmapid"] = iconmapid
    if expand_macros is not None:
        params["expand_macros"] = expand_macros
    if severity_min is not None:
        params["severity_min"] = severity_min
    if private is not None:
        params["private"] = private
    if show_suppressed is not None:
        params["show_suppressed"] = show_suppressed
    if selements is not None:
        params["selements"] = selements
    if links is not None:
        params["links"] = links
    if shapes is not None:
        params["shapes"] = shapes
    if lines is not None:
        params["lines"] = lines
    if users is not None:
        params["users"] = users
    if userGroups is not None:
        params["userGroups"] = userGroups

    result = client.map.update(**params)
    return format_response(result)


@writable_tool()
def map_delete(sysmapids: List[str]) -> str:
    """Delete maps from Zabbix.

    Args:
        sysmapids: List of map IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.map.delete(*sysmapids)
    return format_response(result)


@readonly_tool()
def auto_map_preview(map_name: str,
                    host_group_names: Optional[List[str]] = None,
                    host_group_ids: Optional[List[str]] = None,
                    tag_prefix: str = "am.",
                    layout: str = "grid",
                    width: int = 1920,
                    height: int = 1080,
                    icon_config: Optional[Dict[str, Any]] = None) -> str:
    """Preview automatic topology map based on host tags (read-only, no Zabbix modifications).

    Args:
        map_name: Map name to preview
        host_group_names: Optional list of host group names to include
        host_group_ids: Optional list of host group IDs to include
        tag_prefix: Tag prefix (default: "am.")
        layout: Layout algorithm (grid, circle, tree, drl, fr, kk, random, rt, large_graph)
        width: Map width for preview (default: 1920)
        height: Map height for preview (default: 1080)
        icon_config: Optional icon configuration (uses defaults if not provided)

    Returns:
        JSON string with preview data including hosts, links, and positions
    """
    try:
        result = _auto_map_core(
            map_name=map_name,
            host_group_names=host_group_names,
            host_group_ids=host_group_ids,
            tag_prefix=tag_prefix,
            layout=layout,
            width=width,
            height=height,
            force_relayout=False,
            create_if_missing=False,
            icon_config=icon_config,
            preview_only=True
        )
        return format_response(result)
    except Exception as e:
        logger.error(f"Error in auto_map_preview: {e}")
        return format_response({"error": str(e)})


@writable_tool()
def auto_map_update(map_name: str,
                   host_group_names: Optional[List[str]] = None,
                   host_group_ids: Optional[List[str]] = None,
                   tag_prefix: str = "am.",
                   layout: str = "grid",
                   width: int = 1920,
                   height: int = 1080,
                   force_relayout: bool = False,
                   create_if_missing: bool = True,
                   icon_config: Optional[Dict[str, Any]] = None) -> str:
    """Create or update topology map based on host tags.

    Args:
        map_name: Map name to create/update
        host_group_names: Optional list of host group names to include
        host_group_ids: Optional list of host group IDs to include
        tag_prefix: Tag prefix (default: "am.")
        layout: Layout algorithm (grid, circle, tree, drl, fr, kk, random, rt, large_graph)
        width: Map width for new maps (default: 1920)
        height: Map height for new maps (default: 1080)
        force_relayout: Force recompute all positions (default: False)
        create_if_missing: Create map if it doesn't exist (default: True)
        icon_config: Optional icon configuration (uses defaults if not provided)

    Returns:
        JSON string with result including action taken and map data
    """
    try:
        result = _auto_map_core(
            map_name=map_name,
            host_group_names=host_group_names,
            host_group_ids=host_group_ids,
            tag_prefix=tag_prefix,
            layout=layout,
            width=width,
            height=height,
            force_relayout=force_relayout,
            create_if_missing=create_if_missing,
            icon_config=icon_config,
            preview_only=False
        )
        return format_response(result)
    except Exception as e:
        logger.error(f"Error in auto_map_update: {e}")
        return format_response({"error": str(e)})
