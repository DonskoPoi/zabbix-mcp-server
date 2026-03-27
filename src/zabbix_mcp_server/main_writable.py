"""Zabbix Writable MCP Server - Only write/modification operations.

This server only contains write modification operations (create/update/delete)
for Zabbix API. No query/get operations are available here.
"""

import os
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv

# Import all tools to ensure they register with the registry
from . import tools
from .core import (
    get_transport_config_writable,
    get_auth_provider,
    register_writable_tools,
    get_registered_writable_count,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get auth provider from environment variable configuration
auth = get_auth_provider("WRITABLE")
auth_type = os.getenv("WRITABLE_AUTH_TYPE", "no-auth").lower()
logger.info(f"Writable server auth type: {auth_type}")

mcp = FastMCP("Zabbix Writable MCP Server", auth=auth)

# Register writable tools
register_writable_tools(mcp)


def main():
    logger.info("Starting Zabbix Writable MCP Server")
    try:
        transport_config = get_transport_config_writable()
        logger.info(f"Transport: {transport_config['transport']}")
    except ValueError as e:
        logger.error(f"Transport configuration error: {e}")
        return 1

    logger.info(f"Zabbix URL: {os.getenv('ZABBIX_URL', 'Not configured')}")
    logger.info(f"Registered writable tools: {get_registered_writable_count()}")
    logger.info("Note: This is a writable server - only modification operations are available")

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
