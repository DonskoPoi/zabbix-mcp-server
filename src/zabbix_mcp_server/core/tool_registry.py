"""
Unified tool registry for Zabbix MCP Server.

This module provides a centralized registry for all MCP tools,
with separate registries for read-only and writable tools.
"""

from typing import List, Callable, Any
from dataclasses import dataclass


@dataclass
class _ToolInfo:
    """Information about a registered tool."""
    func: Callable[..., Any]
    category: str  # 'readonly' or 'writable'


# Global registries
_readonly_tools: List[_ToolInfo] = []
_writable_tools: List[_ToolInfo] = []


def _register_tool(func: Callable[..., Any], category: str) -> Callable[..., Any]:
    """Register a tool in the appropriate registry.

    Args:
        func: The tool function to register
        category: Tool category ('readonly' or 'writable')

    Returns:
        The original function (for decorator chaining)
    """
    tool_info = _ToolInfo(func=func, category=category)
    if category == 'readonly':
        _readonly_tools.append(tool_info)
    else:
        _writable_tools.append(tool_info)
    return func


def readonly_tool() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark a function as a read-only tool.

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return _register_tool(func, 'readonly')
    return decorator


def writable_tool() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark a function as a writable tool.

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return _register_tool(func, 'writable')
    return decorator


def register_readonly_tools(mcp: Any) -> None:
    """Register all read-only tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    for tool_info in _readonly_tools:
        mcp.tool()(tool_info.func)


def register_writable_tools(mcp: Any) -> None:
    """Register all writable tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    for tool_info in _writable_tools:
        mcp.tool()(tool_info.func)


def get_registered_readonly_count() -> int:
    """Get the number of registered read-only tools.

    Returns:
        Number of read-only tools
    """
    return len(_readonly_tools)


def get_registered_writable_count() -> int:
    """Get the number of registered writable tools.

    Returns:
        Number of writable tools
    """
    return len(_writable_tools)
