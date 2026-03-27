"""
History management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool


@readonly_tool()
def history_get(itemids: List[str], history: int = 0,
                time_from: Optional[int] = None,
                time_till: Optional[int] = None,
                limit: Optional[int] = None,
                sortfield: str = "clock",
                sortorder: str = "DESC") -> str:
    """Get history data from Zabbix.

    Args:
        itemids: List of item IDs to get history for
        history: History type (0=float, 1=character, 2=log, 3=unsigned, 4=text)
        time_from: Start time (Unix timestamp)
        time_till: End time (Unix timestamp)
        limit: Maximum number of results
        sortfield: Field to sort by
        sortorder: Sort order (ASC or DESC)

    Returns:
        str: JSON formatted history data
    """
    client = get_zabbix_client()
    params = {
        "itemids": itemids,
        "history": history,
        "sortfield": sortfield,
        "sortorder": sortorder
    }

    if time_from:
        params["time_from"] = time_from
    if time_till:
        params["time_till"] = time_till
    if limit:
        params["limit"] = limit

    result = client.history.get(**params)
    return format_response(result)
