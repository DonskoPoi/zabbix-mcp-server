"""
User management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def user_get(userids: Optional[List[str]] = None,
             output: Union[str, List[str]] = "extend",
             search: Optional[Dict[str, str]] = None,
             filter: Optional[Dict[str, Any]] = None) -> str:
    """Get users from Zabbix with optional filtering.

    Args:
        userids: List of user IDs to retrieve
        output: Output format (extend or list of specific fields)
        search: Search criteria
        filter: Filter criteria

    Returns:
        str: JSON formatted list of users
    """
    client = get_zabbix_client()
    params = {"output": output}

    if userids:
        params["userids"] = userids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.user.get(**params)
    return format_response(result)


@writable_tool()
def user_create(username: str, passwd: str, usrgrps: List[Dict[str, str]],
                name: Optional[str] = None, surname: Optional[str] = None,
                email: Optional[str] = None) -> str:
    """Create a new user in Zabbix.

    Args:
        username: Username
        passwd: Password
        usrgrps: List of user groups (format: [{"usrgrpid": "1"}])
        name: First name
        surname: Last name
        email: Email address

    Returns:
        str: JSON formatted creation result
    """
    client = get_zabbix_client()
    params = {
        "username": username,
        "passwd": passwd,
        "usrgrps": usrgrps
    }

    if name:
        params["name"] = name
    if surname:
        params["surname"] = surname
    if email:
        params["email"] = email

    result = client.user.create(**params)
    return format_response(result)


@writable_tool()
def user_update(userid: str, username: Optional[str] = None,
                name: Optional[str] = None, surname: Optional[str] = None,
                email: Optional[str] = None) -> str:
    """Update an existing user in Zabbix.

    Args:
        userid: User ID to update
        username: New username
        name: New first name
        surname: New last name
        email: New email address

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {"userid": userid}

    if username:
        params["username"] = username
    if name:
        params["name"] = name
    if surname:
        params["surname"] = surname
    if email:
        params["email"] = email

    result = client.user.update(**params)
    return format_response(result)


@writable_tool()
def user_delete(userids: List[str]) -> str:
    """Delete users from Zabbix.

    Args:
        userids: List of user IDs to delete

    Returns:
        str: JSON formatted deletion result
    """
    client = get_zabbix_client()
    result = client.user.delete(*userids)
    return format_response(result)
