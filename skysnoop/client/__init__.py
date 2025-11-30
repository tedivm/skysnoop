"""HTTP client for adsb.lol API.

This package provides HTTP client classes for communicating with the adsb.lol API.
Includes the unified SkySnoop client (recommended), plus legacy clients (ReAPIClient
and OpenAPIClient) for backward compatibility.
"""

# Backend adapters
from skysnoop.client.adapters.openapi_adapter import OpenAPIAdapter
from skysnoop.client.adapters.reapi_adapter import ReAPIAdapter

# Legacy clients (backward compatibility)
from skysnoop.client.api import ReAPIClient
from skysnoop.client.base import BaseHTTPClient
from skysnoop.client.openapi import OpenAPIClient

# Primary unified client (recommended)
from skysnoop.client.skysnoop import SkySnoop

__all__ = [
    # Primary interface
    "SkySnoop",
    # Adapters
    "OpenAPIAdapter",
    "ReAPIAdapter",
    # Legacy clients
    "ReAPIClient",
    "BaseHTTPClient",
    "OpenAPIClient",
]
