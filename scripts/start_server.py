#!/usr/bin/env python3
"""
Startup script for Zabbix MCP Server

This script validates the environment configuration and starts the MCP server
with proper error handling and logging.

Author: Zabbix MCP Server Contributors
License: MIT
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def check_environment() -> bool:
    """Check if required environment variables are set.

    Returns:
        bool: True if environment is properly configured
    """
    logger = logging.getLogger(__name__)
    required_vars = ["ZABBIX_URL"]
    missing_vars: List[str] = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables or create a .env file")
        return False

    # Check authentication configuration
    token = os.getenv("ZABBIX_TOKEN")
    user = os.getenv("ZABBIX_USER")
    password = os.getenv("ZABBIX_PASSWORD")

    if not token and not (user and password):
        logger.error("Authentication not configured")
        print("Error: Authentication not configured")
        print("Please set either:")
        print("  - ZABBIX_TOKEN (recommended)")
        print("  - Both ZABBIX_USER and ZABBIX_PASSWORD")
        return False

    return True


def show_server_configuration(prefix: str, name: str, transport_config: Dict[str, Any]) -> None:
    """Display configuration for a specific server.

    Args:
        prefix: Environment variable prefix (e.g., "READONLY" or "WRITABLE")
        name: Human-readable server name
        transport_config: Transport configuration dictionary
    """
    logger = logging.getLogger(__name__)

    print(f"\n{name} Configuration")
    print("-" * 30)

    # Transport configuration
    transport = transport_config["transport"]
    print(f"Transport: {transport}")
    logger.info(f"{name} - Transport: {transport}")

    if transport == 'streamable-http':
        host = transport_config["host"]
        port = transport_config["port"]
        stateless = transport_config["stateless_http"]
        mount_path = transport_config["mount_path"]
        auth_type = os.getenv(f"{prefix}_AUTH_TYPE", "Not set")

        print(f"  - Host: {host}")
        print(f"  - Port: {port}")
        print(f"  - Mount Path: {mount_path}")
        print(f"  - Stateless: {stateless}")
        print(f"  - Auth Type: {auth_type}")

        logger.info(f"{name} HTTP - Host: {host}, Port: {port}, Path: {mount_path}, Stateless: {stateless}")


def show_configuration() -> None:
    """Display current configuration for both servers."""
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 60)
    print("Zabbix MCP Server Configuration")
    print("=" * 60)

    # Zabbix URL (shared)
    zabbix_url = os.getenv('ZABBIX_URL', 'Not configured')
    print(f"\nShared Configuration")
    print("-" * 30)
    print(f"Zabbix URL: {zabbix_url}")
    logger.info(f"Zabbix URL: {zabbix_url}")

    # Authentication method (shared)
    if os.getenv('ZABBIX_TOKEN'):
        auth_method = 'API Token'
        logger.info("Authentication: API Token")
    elif os.getenv('ZABBIX_USER'):
        auth_method = f"Username/Password ({os.getenv('ZABBIX_USER')})"
        logger.info(f"Authentication: Username/Password for user {os.getenv('ZABBIX_USER')}")
    else:
        auth_method = 'Not configured'
        logger.warning("Authentication: Not configured")

    print(f"Authentication: {auth_method}")

    # SSL verification (shared)
    verify_ssl = os.getenv('VERIFY_SSL', 'true').lower() in ('true', '1', 'yes')
    verify_ssl_str = 'Enabled' if verify_ssl else 'Disabled'
    print(f"SSL verification: {verify_ssl_str}")
    logger.info(f"SSL verification: {verify_ssl_str}")

    # Debug mode (shared)
    debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    debug_str = 'Enabled' if debug_mode else 'Disabled'
    print(f"Debug mode: {debug_str}")
    logger.info(f"Debug mode: {debug_str}")

    # Get and show transport configurations
    try:
        from zabbix_mcp_server.core import get_transport_config_readonly, get_transport_config_writable

        readonly_transport = get_transport_config_readonly()
        show_server_configuration("READONLY", "Read-Only Server", readonly_transport)

        writable_transport = get_transport_config_writable()
        show_server_configuration("WRITABLE", "Writable Server", writable_transport)

        # Show tool counts
        from zabbix_mcp_server.core import get_registered_readonly_count, get_registered_writable_count
        print(f"\nRegistered Tools")
        print("-" * 30)
        print(f"Read-Only Tools: {get_registered_readonly_count()}")
        print(f"Writable Tools: {get_registered_writable_count()}")

    except Exception as e:
        logger.warning(f"Could not load complete configuration: {e}")

    print("\n" + "=" * 60)
    print()


def start_readonly_server() -> None:
    """Start the read-only server."""
    logger = logging.getLogger(__name__)
    print("🚀 Starting Read-Only MCP Server...")
    print("Press Ctrl+C to stop")
    print()

    from zabbix_mcp_server.main_readonly import main
    main()


def start_writable_server() -> None:
    """Start the writable server."""
    logger = logging.getLogger(__name__)
    print("🚀 Starting Writable MCP Server...")
    print("Press Ctrl+C to stop")
    print()

    from zabbix_mcp_server.main_writable import main
    main()


def start_both_servers() -> None:
    """Start both servers in the background."""
    logger = logging.getLogger(__name__)
    print("🚀 Starting both Read-Only and Writable MCP Servers in background...")

    processes: List[subprocess.Popen] = []

    try:
        # Start read-only server
        readonly_cmd = [sys.executable, "-m", "uv", "run", "zabbix-mcp-readonly"]
        logger.info(f"Starting read-only server: {' '.join(readonly_cmd)}")
        p_readonly = subprocess.Popen(readonly_cmd)
        processes.append(p_readonly)
        print(f"✅ Read-Only server started (PID: {p_readonly.pid})")

        # Start writable server
        writable_cmd = [sys.executable, "-m", "uv", "run", "zabbix-mcp-writable"]
        logger.info(f"Starting writable server: {' '.join(writable_cmd)}")
        p_writable = subprocess.Popen(writable_cmd)
        processes.append(p_writable)
        print(f"✅ Writable server started (PID: {p_writable.pid})")

        print("\nBoth servers are running in the background.")
        print("Press Ctrl+C to stop both servers.")
        print()

        # Wait for processes
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        logger.info("Stopping servers...")
        print("\n👋 Stopping servers...")
        for p in processes:
            try:
                p.terminate()
                p.wait(timeout=5)
                print(f"✅ Server (PID: {p.pid}) stopped")
            except subprocess.TimeoutExpired:
                p.kill()
                print(f"⚠️ Server (PID: {p.pid}) killed")
    except Exception as e:
        logger.error(f"Error starting servers: {e}")
        print(f"Error starting servers: {e}")
        # Clean up
        for p in processes:
            if p.poll() is None:
                p.terminate()
        sys.exit(1)


def main() -> None:
    """Main startup function."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Zabbix MCP Server Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start read-only server (default)
  %(prog)s -r, --readonly     # Start read-only server
  %(prog)s -w, --writable     # Start writable server
  %(prog)s -a, --all          # Start both servers in background
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--readonly",
        action="store_true",
        help="Start read-only server (default)"
    )
    group.add_argument(
        "-w", "--writable",
        action="store_true",
        help="Start writable server"
    )
    group.add_argument(
        "-a", "--all",
        action="store_true",
        help="Start both servers in background"
    )

    args = parser.parse_args()

    print("Starting Zabbix MCP Server...")
    logger.info("Starting Zabbix MCP Server")

    try:
        # Check environment configuration
        if not check_environment():
            logger.error("Environment validation failed")
            sys.exit(1)

        # Show configuration
        show_configuration()

        # Determine which server(s) to start
        if args.writable:
            start_writable_server()
        elif args.all:
            start_both_servers()
        else:
            # Default to read-only
            start_readonly_server()

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error importing server: {e}")
        print("Please install dependencies: uv sync")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n👋 Server stopped by user")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
