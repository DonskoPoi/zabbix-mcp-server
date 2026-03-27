"""
Trend management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool


@readonly_tool()
def trend_get(itemids: List[str], time_from: Optional[int] = None,
              time_till: Optional[int] = None,
              limit: Optional[int] = None) -> str:
    """Get trend data from Zabbix.

    Args:
        itemids: List of item IDs to get trends for
        time_from: Start time (Unix timestamp)
        time_till: End time (Unix timestamp)
        limit: Maximum number of results

    Returns:
        str: JSON formatted trend data
    """
    client = get_zabbix_client()
    params = {"itemids": itemids}

    if time_from:
        params["time_from"] = time_from
    if time_till:
        params["time_till"] = time_till
    if limit:
        params["limit"] = limit

    result = client.trend.get(**params)
    return format_response(result)
