"""
Template management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def template_get(templateids: Optional[List[str]] = None,
                 groupids: Optional[List[str]] = None,
                 hostids: Optional[List[str]] = None,
                 output: Union[str, List[str]] = "extend",
                 search: Optional[Dict[str, str]] = None,
                 filter: Optional[Dict[str, Any]] = None) -> str:
    """Get templates from Zabbix with optional filtering.

    Args:
        templateids: List of template IDs to retrieve
        groupids: List of host group IDs to filter by
        hostids: List of host IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of templates
    """
    client = get_zabbix_client()
    params = {"output": output}

    if templateids:
        params["templateids"] = templateids
    if groupids:
        params["groupids"] = groupids
    if hostids:
        params["hostids"] = hostids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.template.get(**params)
    return format_response(result)


@writable_tool()
def template_create(host: str, groups: List[Dict[str, str]],
                    name: Optional[str] = None, description: Optional[str] = None) -> str:
    """Create a new template in Zabbix.

    Args:
        host: Template technical name
        groups: List of host groups (format: [{"groupid": "1"}])
        name: Template visible name
        description: Template description

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "host": host,
        "groups": groups
    }

    if name:
        params["name"] = name
    if description:
        params["description"] = description

    result = client.template.create(**params)
    return format_response(result)


@writable_tool()
def template_update(templateid: str, host: Optional[str] = None,
                    name: Optional[str] = None, description: Optional[str] = None) -> str:
    """Update an existing template in Zabbix.

    Args:
        templateid: Template ID to update
        host: New template technical name
        name: New template visible name
        description: New template description

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"templateid": templateid}

    if host:
        params["host"] = host
    if name:
        params["name"] = name
    if description:
        params["description"] = description

    result = client.template.update(**params)
    return format_response(result)


@writable_tool()
def template_delete(templateids: List[str]) -> str:
    """Delete templates from Zabbix.

    Args:
        templateids: List of template IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.template.delete(*templateids)
    return format_response(result)
