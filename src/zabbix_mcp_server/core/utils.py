"""
Utility functions for Zabbix MCP Server.
"""

import json
from typing import Any


def format_response(data: Any) -> str:
    """Format response data as JSON string.

    Args:
        data: Data to format

    Returns:
        str: JSON formatted string
    """
    return json.dumps(data, indent=2, default=str)
