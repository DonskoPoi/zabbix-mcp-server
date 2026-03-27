"""
Zabbix API client management.
"""

import os
import logging
from typing import Optional
from zabbix_utils import ZabbixAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Global Zabbix API client
zabbix_api: Optional[ZabbixAPI] = None


def get_zabbix_client() -> ZabbixAPI:
    """Get or create Zabbix API client with proper authentication.

    Returns:
        ZabbixAPI: Authenticated Zabbix API client

    Raises:
        ValueError: If required environment variables are missing
        Exception: If authentication fails
    """
    global zabbix_api

    if zabbix_api is None:
        url = os.getenv("ZABBIX_URL")
        if not url:
            raise ValueError("ZABBIX_URL environment variable is required")

        logger.info(f"Initializing Zabbix API client for {url}")

        # Configure SSL verification
        verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1", "yes")
        logger.info(f"SSL certificate verification: {'enabled' if verify_ssl else 'disabled'}")

        # Initialize client
        zabbix_api = ZabbixAPI(url=url, validate_certs=verify_ssl)

        # Authenticate using token or username/password
        token = os.getenv("ZABBIX_TOKEN")
        if token:
            logger.info("Authenticating with API token")
            zabbix_api.login(token=token)
        else:
            user = os.getenv("ZABBIX_USER")
            password = os.getenv("ZABBIX_PASSWORD")
            if not user or not password:
                raise ValueError("Either ZABBIX_TOKEN or ZABBIX_USER/ZABBIX_PASSWORD must be set")
            logger.info(f"Authenticating with username: {user}")
            zabbix_api.login(user=user, password=password)

        logger.info("Successfully authenticated with Zabbix API")

    return zabbix_api
