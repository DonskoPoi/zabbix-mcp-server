"""
Proxy management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def proxy_get(proxyids: Optional[List[str]] = None,
              output: str = "extend",
              search: Optional[Dict[str, str]] = None,
              filter: Optional[Dict[str, Any]] = None,
              limit: Optional[int] = None) -> str:
    """Get proxies from Zabbix with optional filtering.

    Args:
        proxyids: List of proxy IDs to retrieve
        output: Output format (extend, shorten, or specific fields)
        search: Search criteria
        filter: Filter criteria
        limit: Maximum number of results

    Returns:
        str: JSON formatted list of proxies
    """
    client = get_zabbix_client()
    params = {"output": output}

    if proxyids:
        params["proxyids"] = proxyids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter
    if limit:
        params["limit"] = limit

    result = client.proxy.get(**params)
    return format_response(result)


@writable_tool()
def proxy_create(host: str, status: int = 5,
                 description: Optional[str] = None,
                 tls_connect: int = 1,
                 tls_accept: int = 1) -> str:
    """Create a new proxy in Zabbix.

    Args:
        host: Proxy name
        status: Proxy status (5=active proxy, 6=passive proxy)
        description: Proxy description
        tls_connect: TLS connection settings (1=no encryption, 2=PSK, 4=certificate)
        tls_accept: TLS accept settings (1=no encryption, 2=PSK, 4=certificate)

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "host": host,
        "status": status,
        "tls_connect": tls_connect,
        "tls_accept": tls_accept
    }

    if description:
        params["description"] = description

    result = client.proxy.create(**params)
    return format_response(result)


@writable_tool()
def proxy_update(proxyid: str, host: Optional[str] = None,
                 status: Optional[int] = None,
                 description: Optional[str] = None,
                 tls_connect: Optional[int] = None,
                 tls_accept: Optional[int] = None) -> str:
    """Update an existing proxy in Zabbix.

    Args:
        proxyid: Proxy ID to update
        host: New proxy name
        status: New proxy status (5=active proxy, 6=passive proxy)
        description: New proxy description
        tls_connect: New TLS connection settings
        tls_accept: New TLS accept settings

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"proxyid": proxyid}

    if host:
        params["host"] = host
    if status is not None:
        params["status"] = status
    if description:
        params["description"] = description
    if tls_connect is not None:
        params["tls_connect"] = tls_connect
    if tls_accept is not None:
        params["tls_accept"] = tls_accept

    result = client.proxy.update(**params)
    return format_response(result)


@writable_tool()
def proxy_delete(proxyids: List[str]) -> str:
    """Delete proxies from Zabbix.

    Args:
        proxyids: List of proxy IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.proxy.delete(*proxyids)
    return format_response(result)
