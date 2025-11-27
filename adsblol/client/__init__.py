"""HTTP client for adsb.lol API.

This package provides HTTP client classes for communicating with the adsb.lol API.
Includes both the re-api client (ADSBLolClient) and OpenAPI client (OpenAPIClient).
"""

from adsblol.client.api import ADSBLolClient
from adsblol.client.base import BaseHTTPClient
from adsblol.client.openapi import OpenAPIClient

__all__ = ["ADSBLolClient", "BaseHTTPClient", "OpenAPIClient"]
