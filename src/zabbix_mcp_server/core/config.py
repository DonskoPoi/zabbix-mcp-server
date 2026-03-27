"""
Configuration management for Zabbix MCP Server.
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def get_auth_provider(prefix: str) -> Optional[Any]:
    """Get auth provider based on environment variable configuration.

    Supports multiple auth types:
    - no-auth: No authentication (auth=None)
    - static-token: Static token authentication (requires *_STATIC_TOKENS)
    - jwt: JWT token authentication (requires additional JWT config)

    Args:
        prefix: Environment variable prefix (e.g., "READONLY" or "WRITABLE")

    Returns:
        Auth provider instance or None for no-auth

    Raises:
        ValueError: If configuration is invalid
        ImportError: If required auth provider classes cannot be imported
    """
    auth_type = os.getenv(f"{prefix}_AUTH_TYPE", "").lower()

    if auth_type in ("", "no-auth"):
        return None

    if auth_type == "static-token":
        # Static token authentication
        tokens_json = os.getenv(f"{prefix}_STATIC_TOKENS")
        if not tokens_json:
            raise ValueError(
                f"{prefix}_STATIC_TOKENS must be set when using static-token auth type"
            )
        try:
            tokens = json.loads(tokens_json)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"{prefix}_STATIC_TOKENS must be valid JSON: {e}"
            )

        from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
        return StaticTokenVerifier(tokens=tokens)

    if auth_type == "jwt":
        # JWT authentication
        jwt_public_key = os.getenv(f"{prefix}_JWT_PUBLIC_KEY")
        jwt_jwks_uri = os.getenv(f"{prefix}_JWT_JWKS_URI")

        if not jwt_public_key and not jwt_jwks_uri:
            raise ValueError(
                f"Either {prefix}_JWT_PUBLIC_KEY or {prefix}_JWT_JWKS_URI "
                f"must be set when using jwt auth type"
            )

        from fastmcp.server.auth.providers.jwt import JWTVerifier

        jwt_kwargs = {}
        if jwt_public_key:
            jwt_kwargs["public_key"] = jwt_public_key
        if jwt_jwks_uri:
            jwt_kwargs["jwks_uri"] = jwt_jwks_uri

        # Optional JWT settings
        jwt_issuer = os.getenv(f"{prefix}_JWT_ISSUER")
        jwt_audience = os.getenv(f"{prefix}_JWT_AUDIENCE")
        jwt_algorithm = os.getenv(f"{prefix}_JWT_ALGORITHM")
        jwt_required_scopes = os.getenv(f"{prefix}_JWT_REQUIRED_SCOPES")

        if jwt_issuer:
            jwt_kwargs["issuer"] = jwt_issuer
        if jwt_audience:
            jwt_kwargs["audience"] = jwt_audience
        if jwt_algorithm:
            jwt_kwargs["algorithm"] = jwt_algorithm
        if jwt_required_scopes:
            from fastmcp.utilities.auth import parse_scopes
            jwt_kwargs["required_scopes"] = parse_scopes(jwt_required_scopes)

        return JWTVerifier(**jwt_kwargs)

    raise ValueError(
        f"Invalid {prefix}_AUTH_TYPE: {auth_type}. "
        f"Must be one of: no-auth, static-token, jwt"
    )


def _get_transport_config(prefix: str, default_port: int) -> Dict[str, Any]:
    """Get transport configuration from environment variables with a given prefix.

    Args:
        prefix: Environment variable prefix (e.g., "READONLY" or "WRITABLE")
        default_port: Default port for HTTP transport

    Returns:
        Transport configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    transport = os.getenv(f"{prefix}_TRANSPORT", "stdio")

    if transport not in ["stdio", "streamable-http"]:
        raise ValueError(
            f"Invalid {prefix}_TRANSPORT: {transport}. Must be 'stdio' or 'streamable-http'"
        )

    config = {"transport": transport}

    if transport == "streamable-http":
        # Get HTTP configuration with defaults
        config.update({
            "host": os.getenv(f"{prefix}_HOST", "0.0.0.0"),
            "port": int(os.getenv(f"{prefix}_PORT", str(default_port))),
            "stateless_http": os.getenv(f"{prefix}_STATELESS_HTTP", "false").lower() in ("true", "1", "yes"),
            "mount_path": os.getenv(f"{prefix}_MOUNTPATH", "/")
        })

        logger.info(
            f"{prefix} HTTP transport configured: {config['host']}:{config['port']}, "
            f"stateless_http={config['stateless_http']}"
        )

    return config


def get_transport_config_readonly() -> Dict[str, Any]:
    """Get transport configuration for the read-only server.

    Returns:
        Dict[str, Any]: Transport configuration for read-only server

    Raises:
        ValueError: If configuration is invalid
    """
    return _get_transport_config("READONLY", 9002)


def get_transport_config_writable() -> Dict[str, Any]:
    """Get transport configuration for the writable server.

    Returns:
        Dict[str, Any]: Transport configuration for writable server

    Raises:
        ValueError: If configuration is invalid
    """
    return _get_transport_config("WRITABLE", 9003)
