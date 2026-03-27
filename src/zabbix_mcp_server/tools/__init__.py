"""
Tools package for Zabbix MCP Server.

This package contains all the Zabbix MCP tools organized by category.
When this package is imported, all tool modules are loaded and register
their tools with the centralized tool registry.
"""

# Import all tool modules to ensure they register themselves
# with the centralized tool registry
from . import host
from . import hostgroup
from . import item
from . import trigger
from . import template
from . import problem
from . import event
from . import history
from . import trend
from . import user
from . import proxy
from . import maintenance
from . import graph
from . import valuemap
from . import discovery
from . import itemprototype
from . import configuration
from . import macro
from . import map
from . import dashboard
from . import system
from . import mediatype
from . import action
from . import usermedia

__all__ = []
