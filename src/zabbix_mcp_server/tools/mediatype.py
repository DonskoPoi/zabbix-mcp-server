"""
Media type management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def mediatype_get(mediatypeids: Optional[List[str]] = None,
                  output: Union[str, List[str]] = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None) -> str:
    """Get media types from Zabbix with optional filtering.

    Args:
        mediatypeids: List of media type IDs to retrieve
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of media types
    """
    client = get_zabbix_client()
    params = {"output": output}

    if mediatypeids:
        params["mediatypeids"] = mediatypeids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.mediatype.get(**params)
    return format_response(result)


@writable_tool()
def mediatype_create(name: str,
                     type: int,
                     parameters: Optional[List[Dict[str, str]]] = None,
                     script: Optional[str] = None,
                     smtp_server: Optional[str] = None,
                     smtp_helo: Optional[str] = None,
                     smtp_email: Optional[str] = None,
                     smtp_port: Optional[str] = None,
                     smtp_security: Optional[int] = None,
                     smtp_verify_peer: Optional[int] = None,
                     smtp_verify_host: Optional[int] = None,
                     smtp_authentication: Optional[int] = None,
                     username: Optional[str] = None,
                     passwd: Optional[str] = None,
                     exec_path: Optional[str] = None,
                     gsm_modem: Optional[str] = None,
                     status: Optional[int] = None,
                     maxsessions: Optional[int] = None,
                     maxattempts: Optional[int] = None,
                     attempt_interval: Optional[str] = None,
                     message_format: Optional[int] = None,
                     message_templates: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a new media type in Zabbix.

    Args:
        name: Media type name
        type: Media type (0=Email, 1=Script, 2=SMS, 4=Webhook)
        parameters: Webhook parameters (for type 4) - list of {"name": "...", "value": "..."}
        script: JavaScript script for webhook (for type 4)
        smtp_server: SMTP server (for type 0)
        smtp_helo: SMTP helo (for type 0)
        smtp_email: SMTP email (for type 0)
        smtp_port: SMTP port (for type 0)
        smtp_security: SMTP security (for type 0)
        smtp_verify_peer: SMTP verify peer (for type 0)
        smtp_verify_host: SMTP verify host (for type 0)
        smtp_authentication: SMTP authentication (for type 0)
        username: Username for SMTP authentication (for type 0)
        passwd: Password for SMTP authentication (for type 0)
        exec_path: Executable path (for type 1)
        gsm_modem: GSM modem (for type 2)
        status: Status (0=enabled, 1=disabled)
        maxsessions: Max concurrent sessions
        maxattempts: Max attempts
        attempt_interval: Attempt interval
        message_format: Message format (0=HTML, 1=Text)
        message_templates: Message templates

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "name": name,
        "type": type
    }

    if parameters is not None:
        params["parameters"] = parameters
    if script is not None:
        params["script"] = script
    if smtp_server is not None:
        params["smtp_server"] = smtp_server
    if smtp_helo is not None:
        params["smtp_helo"] = smtp_helo
    if smtp_email is not None:
        params["smtp_email"] = smtp_email
    if smtp_port is not None:
        params["smtp_port"] = smtp_port
    if smtp_security is not None:
        params["smtp_security"] = smtp_security
    if smtp_verify_peer is not None:
        params["smtp_verify_peer"] = smtp_verify_peer
    if smtp_verify_host is not None:
        params["smtp_verify_host"] = smtp_verify_host
    if smtp_authentication is not None:
        params["smtp_authentication"] = smtp_authentication
    if username is not None:
        params["username"] = username
    if passwd is not None:
        params["passwd"] = passwd
    if exec_path is not None:
        params["exec_path"] = exec_path
    if gsm_modem is not None:
        params["gsm_modem"] = gsm_modem
    if status is not None:
        params["status"] = status
    if maxsessions is not None:
        params["maxsessions"] = maxsessions
    if maxattempts is not None:
        params["maxattempts"] = maxattempts
    if attempt_interval is not None:
        params["attempt_interval"] = attempt_interval
    if message_format is not None:
        params["message_format"] = message_format
    if message_templates is not None:
        params["message_templates"] = message_templates

    result = client.mediatype.create(**params)
    return format_response(result)


@writable_tool()
def mediatype_update(mediatypeid: str,
                     name: Optional[str] = None,
                     parameters: Optional[List[Dict[str, str]]] = None,
                     script: Optional[str] = None,
                     smtp_server: Optional[str] = None,
                     smtp_helo: Optional[str] = None,
                     smtp_email: Optional[str] = None,
                     smtp_port: Optional[str] = None,
                     smtp_security: Optional[int] = None,
                     smtp_verify_peer: Optional[int] = None,
                     smtp_verify_host: Optional[int] = None,
                     smtp_authentication: Optional[int] = None,
                     username: Optional[str] = None,
                     passwd: Optional[str] = None,
                     exec_path: Optional[str] = None,
                     gsm_modem: Optional[str] = None,
                     status: Optional[int] = None,
                     maxsessions: Optional[int] = None,
                     maxattempts: Optional[int] = None,
                     attempt_interval: Optional[str] = None,
                     message_format: Optional[int] = None,
                     message_templates: Optional[List[Dict[str, Any]]] = None) -> str:
    """Update an existing media type in Zabbix.

    Args:
        mediatypeid: Media type ID to update
        name: New media type name
        parameters: Webhook parameters (for type 4)
        script: JavaScript script for webhook (for type 4)
        smtp_server: SMTP server (for type 0)
        smtp_helo: SMTP helo (for type 0)
        smtp_email: SMTP email (for type 0)
        smtp_port: SMTP port (for type 0)
        smtp_security: SMTP security (for type 0)
        smtp_verify_peer: SMTP verify peer (for type 0)
        smtp_verify_host: SMTP verify host (for type 0)
        smtp_authentication: SMTP authentication (for type 0)
        username: Username for SMTP authentication (for type 0)
        passwd: Password for SMTP authentication (for type 0)
        exec_path: Executable path (for type 1)
        gsm_modem: GSM modem (for type 2)
        status: Status (0=enabled, 1=disabled)
        maxsessions: Max concurrent sessions
        maxattempts: Max attempts
        attempt_interval: Attempt interval
        message_format: Message format (0=HTML, 1=Text)
        message_templates: Message templates

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"mediatypeid": mediatypeid}

    if name is not None:
        params["name"] = name
    if parameters is not None:
        params["parameters"] = parameters
    if script is not None:
        params["script"] = script
    if smtp_server is not None:
        params["smtp_server"] = smtp_server
    if smtp_helo is not None:
        params["smtp_helo"] = smtp_helo
    if smtp_email is not None:
        params["smtp_email"] = smtp_email
    if smtp_port is not None:
        params["smtp_port"] = smtp_port
    if smtp_security is not None:
        params["smtp_security"] = smtp_security
    if smtp_verify_peer is not None:
        params["smtp_verify_peer"] = smtp_verify_peer
    if smtp_verify_host is not None:
        params["smtp_verify_host"] = smtp_verify_host
    if smtp_authentication is not None:
        params["smtp_authentication"] = smtp_authentication
    if username is not None:
        params["username"] = username
    if passwd is not None:
        params["passwd"] = passwd
    if exec_path is not None:
        params["exec_path"] = exec_path
    if gsm_modem is not None:
        params["gsm_modem"] = gsm_modem
    if status is not None:
        params["status"] = status
    if maxsessions is not None:
        params["maxsessions"] = maxsessions
    if maxattempts is not None:
        params["maxattempts"] = maxattempts
    if attempt_interval is not None:
        params["attempt_interval"] = attempt_interval
    if message_format is not None:
        params["message_format"] = message_format
    if message_templates is not None:
        params["message_templates"] = message_templates

    result = client.mediatype.update(**params)
    return format_response(result)


@writable_tool()
def mediatype_delete(mediatypeids: List[str]) -> str:
    """Delete media types from Zabbix.

    Args:
        mediatypeids: List of media type IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.mediatype.delete(*mediatypeids)
    return format_response(result)
