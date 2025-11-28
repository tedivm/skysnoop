"""HTTP client for adsb.lol API.

This package provides HTTP client classes for communicating with the adsb.lol API.
Includes both the re-api client (ReAPIClient) and OpenAPI client (OpenAPIClient).
"""

from skysnoop.client.api import ReAPIClient
from skysnoop.client.base import BaseHTTPClient
from skysnoop.client.openapi import OpenAPIClient

__all__ = ["ReAPIClient", "BaseHTTPClient", "OpenAPIClient"]
