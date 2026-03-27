"""
Host management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def host_get(hostids: Optional[List[str]] = None,
             groupids: Optional[List[str]] = None,
             templateids: Optional[List[str]] = None,
             output: Union[str, List[str]] = "extend",
             search: Optional[Dict[str, str]] = None,
             filter: Optional[Dict[str, Any]] = None,
             limit: Optional[int] = None,
             selectInterfaces: Optional[Union[str, List[str]]] = None,
             selectTags: Optional[Union[str, List[str]]] = None,
             selectInheritedTags: Optional[Union[str, List[str]]] = None,
             selectGroups: Optional[Union[str, List[str]]] = None,
             selectTemplates: Optional[Union[str, List[str]]] = None,
             selectMacros: Optional[Union[str, List[str]]] = None,
             selectInventory: Optional[Union[str, List[str]]] = None,
             selectParentTemplates: Optional[Union[str, List[str]]] = None,
             selectDiscoveries: Optional[Union[str, List[str]]] = None,
             selectDiscoveryRule: Optional[Union[str, List[str]]] = None,
             selectHttpTests: Optional[Union[str, List[str]]] = None,
             selectItems: Optional[Union[str, List[str]]] = None,
             selectTriggers: Optional[Union[str, List[str]]] = None,
             selectGraphs: Optional[Union[str, List[str]]] = None,
             selectApplications: Optional[Union[str, List[str]]] = None,
             selectScreens: Optional[Union[str, List[str]]] = None) -> str:
    """Get hosts from Zabbix with optional filtering.

    Args:
        hostids: List of host IDs to retrieve
        groupids: List of host group IDs to filter by
        templateids: List of template IDs to filter by
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results
        selectInterfaces: Return host interfaces
        selectTags: Return host tags
        selectInheritedTags: Return tags inherited from templates
        selectGroups: Return host groups
        selectTemplates: Return linked templates
        selectMacros: Return host macros
        selectInventory: Return host inventory
        selectParentTemplates: Return parent templates
        selectDiscoveries: Return LLD rules
        selectDiscoveryRule: Return discovery rule (for discovered hosts)
        selectHttpTests: Return web scenarios
        selectItems: Return items
        selectTriggers: Return triggers
        selectGraphs: Return graphs
        selectApplications: Return applications
        selectScreens: Return screens

    Returns:
        str: JSON formatted list of hosts
    """
    client = get_zabbix_client()
    params = {"output": output}

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
    if selectInterfaces is not None:
        params["selectInterfaces"] = selectInterfaces
    if selectTags is not None:
        params["selectTags"] = selectTags
    if selectInheritedTags is not None:
        params["selectInheritedTags"] = selectInheritedTags
    if selectGroups is not None:
        params["selectGroups"] = selectGroups
    if selectTemplates is not None:
        params["selectTemplates"] = selectTemplates
    if selectMacros is not None:
        params["selectMacros"] = selectMacros
    if selectInventory is not None:
        params["selectInventory"] = selectInventory
    if selectParentTemplates is not None:
        params["selectParentTemplates"] = selectParentTemplates
    if selectDiscoveries is not None:
        params["selectDiscoveries"] = selectDiscoveries
    if selectDiscoveryRule is not None:
        params["selectDiscoveryRule"] = selectDiscoveryRule
    if selectHttpTests is not None:
        params["selectHttpTests"] = selectHttpTests
    if selectItems is not None:
        params["selectItems"] = selectItems
    if selectTriggers is not None:
        params["selectTriggers"] = selectTriggers
    if selectGraphs is not None:
        params["selectGraphs"] = selectGraphs
    if selectApplications is not None:
        params["selectApplications"] = selectApplications
    if selectScreens is not None:
        params["selectScreens"] = selectScreens

    result = client.host.get(**params)
    return format_response(result)


@writable_tool()
def host_create(host: str, groups: List[Dict[str, str]],
                interfaces: List[Dict[str, Any]],
                name: Optional[str] = None,
                templates: Optional[List[Dict[str, str]]] = None,
                tags: Optional[List[Dict[str, str]]] = None,
                macros: Optional[List[Dict[str, Any]]] = None,
                inventory_mode: int = -1,
                inventory: Optional[Dict[str, Any]] = None,
                status: int = 0,
                tls_connect: Optional[int] = None,
                tls_accept: Optional[int] = None,
                tls_psk_identity: Optional[str] = None,
                tls_psk: Optional[str] = None,
                tls_issuer: Optional[str] = None,
                tls_subject: Optional[str] = None,
                monitored_by: Optional[int] = None,
                proxyid: Optional[int] = None,
                proxy_groupid: Optional[int] = None) -> str:
    """Create a new host in Zabbix.

    Args:
        host: Host technical name
        groups: List of host groups (format: [{"groupid": "1"}])
        interfaces: List of host interfaces. Each interface should contain:
            - type: 1=Zabbix agent, 2=SNMP, 3=IPMI, 4=JMX
            - main: 1=default interface, 0=secondary
            - useip: 1=connect via IP, 0=connect via DNS
            - ip: IP address (used if useip=1)
            - dns: DNS name (used if useip=0)
            - port: Port number (agent: 10050, SNMP: 161)
            - details: For SNMP interfaces, contains SNMP version etc.
        name: Host visible name
        templates: List of templates to link (format: [{"templateid": "1"}])
        tags: List of host tags (format: [{"tag": "name", "value": "value"}])
        macros: List of user macros (format: [{"macro": "{$MACRO}", "value": "val"}])
        inventory_mode: Inventory mode (-1=disabled, 0=manual, 1=automatic)
        inventory: Host inventory properties dictionary
        status: Host status (0=enabled, 1=disabled)
        tls_connect: Connection encryption (1=no encryption, 2=PSK, 4=certificate)
        tls_accept: Acceptable encryption types (bitmask: 1=no, 2=PSK, 4=certificate)
        tls_psk_identity: PSK identity string
        tls_psk: Pre-shared key (hex string)
        tls_issuer: Certificate issuer
        tls_subject: Certificate subject
        monitored_by: Who monitors the host (0=server, 1=proxy, 2=proxy group)
        proxyid: Proxy ID (used if monitored_by=1)
        proxy_groupid: Proxy group ID (used if monitored_by=2)

    Returns:
        str: JSON formatted creation result containing hostids

    Example:
        Creating a Zabbix agent host:
        {
            "host": "Linux server",
            "interfaces": [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "192.168.3.1",
                "dns": "",
                "port": "10050"
            }],
            "groups": [{"groupid": "50"}]
        }
    """
    client = get_zabbix_client()
    params = {
        "host": host,
        "groups": groups,
        "interfaces": interfaces,
        "inventory_mode": inventory_mode,
        "status": status
    }

    if name is not None:
        params["name"] = name
    if templates:
        params["templates"] = templates
    if tags:
        params["tags"] = tags
    if macros:
        params["macros"] = macros
    if inventory is not None:
        params["inventory"] = inventory
    if tls_connect is not None:
        params["tls_connect"] = tls_connect
    if tls_accept is not None:
        params["tls_accept"] = tls_accept
    if tls_psk_identity is not None:
        params["tls_psk_identity"] = tls_psk_identity
    if tls_psk is not None:
        params["tls_psk"] = tls_psk
    if tls_issuer is not None:
        params["tls_issuer"] = tls_issuer
    if tls_subject is not None:
        params["tls_subject"] = tls_subject
    if monitored_by is not None:
        params["monitored_by"] = monitored_by
    if proxyid is not None:
        params["proxyid"] = proxyid
    if proxy_groupid is not None:
        params["proxy_groupid"] = proxy_groupid

    result = client.host.create(**params)
    return format_response(result)


@writable_tool()
def host_update(hostid: str, host: Optional[str] = None,
                name: Optional[str] = None, status: Optional[int] = None) -> str:
    """Update an existing host in Zabbix.

    Args:
        hostid: Host ID to update
        host: New host name
        name: New visible name
        status: New status (0=enabled, 1=disabled)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"hostid": hostid}

    if host:
        params["host"] = host
    if name:
        params["name"] = name
    if status is not None:
        params["status"] = status

    result = client.host.update(**params)
    return format_response(result)


@writable_tool()
def host_delete(hostids: List[str]) -> str:
    """Delete hosts from Zabbix.

    Args:
        hostids: List of host IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.host.delete(*hostids)
    return format_response(result)
