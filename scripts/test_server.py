#!/usr/bin/env python3
"""
Test script for Zabbix MCP Server

This script validates the server configuration and tests basic functionality
to ensure everything is working correctly.

Author: Zabbix MCP Server Contributors
License: MIT
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def test_import(server_type: str = "readonly") -> bool:
    """Test if the server module can be imported.

    Args:
        server_type: Type of server to test ("readonly" or "writable")

    Returns:
        bool: True if import successful
    """
    try:
        print("🔍 Testing module import...")
        # Test core imports
        from zabbix_mcp_server.core import get_zabbix_client
        # Test main imports based on server type
        if server_type == "readonly":
            from zabbix_mcp_server.main_readonly import main as readonly_main
            print("✅ Read-only module import successful")
        else:
            from zabbix_mcp_server.main_writable import main as writable_main
            print("✅ Writable module import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Please install dependencies: uv sync")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False


def test_environment(server_type: str = "readonly") -> bool:
    """Test environment configuration.

    Args:
        server_type: Type of server to test ("readonly" or "writable")

    Returns:
        bool: True if environment is properly configured
    """
    print(f"\n🔍 Testing {server_type} environment configuration...")

    # Check required variables
    zabbix_url = os.getenv("ZABBIX_URL")
    if not zabbix_url:
        print("❌ ZABBIX_URL not configured")
        return False

    print(f"✅ ZABBIX_URL: {zabbix_url}")

    # Check authentication
    token = os.getenv("ZABBIX_TOKEN")
    user = os.getenv("ZABBIX_USER")
    password = os.getenv("ZABBIX_PASSWORD")

    if token:
        print("✅ Authentication: API Token configured")
    elif user and password:
        print(f"✅ Authentication: Username/Password configured ({user})")
    else:
        print("❌ Authentication not configured")
        print("Please set either ZABBIX_TOKEN or both ZABBIX_USER and ZABBIX_PASSWORD")
        return False

    # Check SSL verification
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1", "yes")
    print(f"ℹ️  SSL verification: {'Enabled' if verify_ssl else 'Disabled'}")

    return True


def test_transport_config(server_type: str = "readonly") -> bool:
    """Test transport configuration.

    Args:
        server_type: Type of server to test ("readonly" or "writable")

    Returns:
        bool: True if transport configuration is valid
    """
    print(f"\n🔍 Testing {server_type} transport configuration...")

    try:
        from zabbix_mcp_server.core import (
            get_transport_config_readonly,
            get_transport_config_writable,
        )

        if server_type == "readonly":
            config = get_transport_config_readonly()
            prefix = "READONLY"
        else:
            config = get_transport_config_writable()
            prefix = "WRITABLE"

        transport = config["transport"]
        print(f"✅ Transport type: {transport}")

        if transport == "streamable-http":
            print(f"  - Host: {config['host']}")
            print(f"  - Port: {config['port']}")
            print(f"  - Stateless: {config['stateless_http']}")
            print(f"  - Mount Path: {config['mount_path']}")

            # Check AUTH_TYPE requirement
            auth_type = os.getenv(f"{prefix}_AUTH_TYPE", "").lower()
            if auth_type == "no-auth":
                print("  ✅ AUTH_TYPE correctly set to 'no-auth'")
            else:
                print(f"  ❌ {prefix}_AUTH_TYPE must be set to 'no-auth' for HTTP transport")
                return False
        else:
            print("  ✅ STDIO transport configured correctly")

        return True

    except ValueError as e:
        print(f"❌ Transport configuration error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error testing transport: {e}")
        return False


def test_connection() -> bool:
    """Test basic connection to Zabbix.

    Returns:
        bool: True if connection successful
    """
    print("\n🔍 Testing Zabbix connection...")

    try:
        from zabbix_mcp_server.core import get_zabbix_client

        # Test getting client and API version
        client = get_zabbix_client()
        version_info = client.apiinfo.version()

        print(f"✅ Connected to Zabbix API version: {version_info}")
        return True

    except ValueError as e:
        if "environment variable" in str(e).lower():
            print(f"❌ Configuration error: {e}")
        else:
            print(f"❌ Connection failed: {e}")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_basic_operations(server_type: str = "readonly") -> bool:
    """Test basic operations for the specified server type.

    Args:
        server_type: Type of server to test ("readonly" or "writable")

    Returns:
        bool: True if operations successful
    """
    print(f"\n🔍 Testing {server_type} operations...")

    try:
        from zabbix_mcp_server.core import get_zabbix_client, get_registered_readonly_count, get_registered_writable_count

        if server_type == "readonly":
            tool_count = get_registered_readonly_count()
            print(f"✅ Registered read-only tools: {tool_count}")

            client = get_zabbix_client()

            # Test host groups (usually always present)
            print("  - Testing host group retrieval...")
            groups = client.hostgroup.get(limit=1)
            if groups:
                print(f"    ✅ Retrieved {len(groups)} host group(s)")
            else:
                print("    ⚠️  No host groups found (this might be normal)")

            # Test hosts
            print("  - Testing host retrieval...")
            hosts = client.host.get(limit=1)
            if hosts:
                print(f"    ✅ Retrieved {len(hosts)} host(s)")
            else:
                print("    ⚠️  No hosts found (this might be normal)")

            # Test items
            print("  - Testing item retrieval...")
            items = client.item.get(limit=1)
            if items:
                print(f"    ✅ Retrieved {len(items)} item(s)")
            else:
                print("    ⚠️  No items found (this might be normal)")
        else:
            tool_count = get_registered_writable_count()
            print(f"✅ Registered writable tools: {tool_count}")
            print("  ℹ️  Writable server only includes modification operations")
            print("  ℹ️  Skipping actual write operations to avoid unintended changes")

        print(f"✅ {server_type.capitalize()} operations test successful")
        return True

    except Exception as e:
        print(f"❌ {server_type.capitalize()} operations failed: {e}")
        return False


def show_summary(tests_passed: int, total_tests: int, server_type: str) -> None:
    """Show test summary.

    Args:
        tests_passed: Number of tests that passed
        total_tests: Total number of tests
        server_type: Type of server that was tested
    """
    print("\n" + "=" * 50)
    print(f"TEST SUMMARY - {server_type.upper()} SERVER")
    print("=" * 50)

    if tests_passed == total_tests:
        print(f"🎉 All {total_tests} tests passed!")
        print(f"✅ The Zabbix MCP {server_type.capitalize()} Server is ready to use")

        print("\nNext steps:")
        print(f"1. Start the {server_type} server:")
        if server_type == "readonly":
            print("   uv run python scripts/start_server.py --readonly")
        else:
            print("   uv run python scripts/start_server.py --writable")
        print("2. Or start both servers: uv run python scripts/start_server.py --all")
        print("3. Test with your MCP client")

    else:
        print(f"❌ {tests_passed}/{total_tests} tests passed")
        print("Please fix the issues above before using the server")

    print("=" * 50)


def main() -> None:
    """Main test function."""
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Zabbix MCP Server Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Test read-only server (default)
  %(prog)s -r, --readonly     # Test read-only server
  %(prog)s -w, --writable     # Test writable server
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--readonly",
        action="store_true",
        help="Test read-only server (default)"
    )
    group.add_argument(
        "-w", "--writable",
        action="store_true",
        help="Test writable server"
    )

    args = parser.parse_args()
    server_type = "writable" if args.writable else "readonly"

    print(f"🧪 Zabbix MCP Server Test Suite - {server_type.capitalize()}")
    print("=" * 50)

    tests = [
        ("Module Import", lambda: test_import(server_type)),
        ("Environment Configuration", lambda: test_environment(server_type)),
        ("Transport Configuration", lambda: test_transport_config(server_type)),
        ("Zabbix Connection", test_connection),
        ("Basic Operations", lambda: test_basic_operations(server_type)),
    ]

    tests_passed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                tests_passed += 1
        except KeyboardInterrupt:
            print("\n\n⏹️  Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")

    show_summary(tests_passed, len(tests), server_type)

    # Exit with appropriate code
    if tests_passed == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
