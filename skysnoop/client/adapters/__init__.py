"""Backend adapters for SkySnoop unified client.

This package provides adapter implementations that wrap existing clients
(OpenAPIClient, ReAPIClient) to conform to the BackendProtocol interface.
"""

from .openapi_adapter import OpenAPIAdapter
from .reapi_adapter import ReAPIAdapter

__all__ = ["OpenAPIAdapter", "ReAPIAdapter"]
