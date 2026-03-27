"""Zabbix Read-Only MCP Server - Only query/get operations.

This server only contains read-only query operations to Zabbix API.
No create/update/delete operations are available.
"""

import os
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv

# Import all tools to ensure they register with the registry
from . import tools
from .core import (
    get_transport_config_readonly,
    get_auth_provider,
    register_readonly_tools,
    get_registered_readonly_count,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get auth provider from environment variable configuration
auth = get_auth_provider("READONLY")
auth_type = os.getenv("READONLY_AUTH_TYPE", "no-auth").lower()
logger.info(f"Read-Only server auth type: {auth_type}")

mcp = FastMCP("Zabbix Read-Only MCP Server", auth=auth)

# Register read-only tools
register_readonly_tools(mcp)


def main():
    logger.info("Starting Zabbix Read-Only MCP Server")
    try:
        transport_config = get_transport_config_readonly()
        logger.info(f"Transport: {transport_config['transport']}")
    except ValueError as e:
        logger.error(f"Transport configuration error: {e}")
        return 1

    logger.info(f"Zabbix URL: {os.getenv('ZABBIX_URL', 'Not configured')}")
    logger.info(f"Registered read-only tools: {get_registered_readonly_count()}")
    logger.info("Note: This is a read-only server - only query operations are available")

    try:
        if transport_config["transport"] == "stdio":
            mcp.run()
        else:
            mcp.run(
                transport="streamable-http",
                host=transport_config["host"],
                port=transport_config["port"],
                stateless_http=transport_config["stateless_http"],
                path=transport_config['mount_path']
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
