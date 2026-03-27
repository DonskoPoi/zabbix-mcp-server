"""
Configuration export/import tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def configuration_export(format: str = "json",
                         options: Optional[Dict[str, Any]] = None) -> str:
    """Export configuration from Zabbix.

    Args:
        format: Export format (json, xml)
        options: Export options

    Returns:
        str: JSON formatted export result
    """
    client = get_zabbix_client()
    params = {"format": format}

    if options:
        params["options"] = options

    result = client.configuration.export(**params)
    return format_response(result)


@writable_tool()
def configuration_import(format: str, source: str,
                         rules: Dict[str, Any]) -> str:
    """Import configuration to Zabbix.

    Args:
        format: Import format (json, xml)
        source: Configuration data to import
        rules: Import rules

    Returns:
        str: JSON formatted import result
    """
    client = get_zabbix_client()
    params = {
        "format": format,
        "source": source,
        "rules": rules
    }

    result = client.configuration.import_(**params)
    return format_response(result)
