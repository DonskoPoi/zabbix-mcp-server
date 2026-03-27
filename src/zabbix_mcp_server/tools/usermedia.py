"""
User media management tools for Zabbix MCP Server.
"""

from typing import Any, Dict, List, Optional, Union
from ..core import get_zabbix_client, format_response, readonly_tool, writable_tool


@readonly_tool()
def usermedia_get(userids: Optional[List[str]] = None,
                  output: Union[str, List[str]] = "extend",
                  selectMedias: Optional[Union[str, List[str]]] = "extend",
                  search: Optional[Dict[str, str]] = None,
                  filter: Optional[Dict[str, Any]] = None) -> str:
    """Get user media (media types assigned to users) from Zabbix.

    Args:
        userids: List of user IDs to retrieve media for
        output: Output format (extend or list of specific fields)
        selectMedias: Return user media (default: "extend")
        search: Search criteria for users
        filter: Filter criteria for users

    Returns:
        str: JSON formatted list of users with their media
    """
    client = get_zabbix_client()
    params = {
        "output": output,
        "selectMedias": selectMedias
    }

    if userids:
        params["userids"] = userids
    if search:
        params["search"] = search
    if filter:
        params["filter"] = filter

    result = client.user.get(**params)
    return format_response(result)


@writable_tool()
def usermedia_add(userid: str,
                  mediatypeid: str,
                  sendto: str,
                  active: int = 0,
                  severity: Optional[int] = None,
                  period: Optional[str] = None) -> str:
    """Add a media type to a user.

    Args:
        userid: User ID to add media to
        mediatypeid: Media type ID
        sendto: Send to address/value (can be dummy for webhook)
        active: Whether media is active (0=enabled, 1=disabled)
        severity: Severity bitmask (1=Not classified, 2=Information, 4=Warning, 8=Average, 16=High, 32=Disaster, 63=All)
        period: Time when the media is active (e.g., "1-7,00:00-24:00")

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()

    # First get the user's current media
    current_user = client.user.get(
        userids=[userid],
        selectMedias="extend"
    )

    user_medias = []
    if current_user and len(current_user) > 0 and "medias" in current_user[0]:
        user_medias = current_user[0]["medias"]

    # Create new media entry
    new_media = {
        "mediatypeid": mediatypeid,
        "sendto": sendto,
        "active": active
    }

    if severity is not None:
        new_media["severity"] = severity
    if period is not None:
        new_media["period"] = period

    # Add the new media to existing ones
    user_medias.append(new_media)

    # Update the user
    params = {
        "userid": userid,
        "medias": user_medias
    }

    result = client.user.update(**params)
    return format_response(result)


@writable_tool()
def usermedia_update(userid: str,
                     medias: List[Dict[str, Any]]) -> str:
    """Update all media for a user (replaces existing media).

    Args:
        userid: User ID to update media for
        medias: Complete list of user media (replaces existing)
            Each media should have:
            - mediatypeid: Media type ID
            - sendto: Send to address/value
            - active: 0=enabled, 1=disabled
            - severity: (optional) Severity bitmask
            - period: (optional) Active period

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()
    params = {
        "userid": userid,
        "medias": medias
    }

    result = client.user.update(**params)
    return format_response(result)


@writable_tool()
def usermedia_remove(userid: str,
                     mediatypeid: Optional[str] = None) -> str:
    """Remove media from a user.

    Args:
        userid: User ID to remove media from
        mediatypeid: Media type ID to remove (if None, removes all media)

    Returns:
        str: JSON formatted update result
    """
    client = get_zabbix_client()

    # First get the user's current media
    current_user = client.user.get(
        userids=[userid],
        selectMedias="extend"
    )

    if not current_user or len(current_user) == 0 or "medias" not in current_user[0]:
        return format_response({"message": "No media found for user"})

    user_medias = current_user[0]["medias"]

    if mediatypeid is None:
        # Remove all media
        new_medias = []
    else:
        # Keep only media that doesn't match the mediatypeid
        new_medias = [
            m for m in user_medias
            if m.get("mediatypeid") != mediatypeid
        ]

    # Update the user
    params = {
        "userid": userid,
        "medias": new_medias
    }

    result = client.user.update(**params)
    return format_response(result)
