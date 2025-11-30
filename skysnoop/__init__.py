try:
    from . import _version

    __version__ = _version.__version__
except:  # noqa: E722
    __version__ = "0.0.0-dev"

# Legacy clients (backward compatibility)
from skysnoop.client.api import ReAPIClient
from skysnoop.client.openapi import OpenAPIClient

# Primary unified client interface (recommended)
from skysnoop.client.skysnoop import SkySnoop

# Exceptions
from skysnoop.exceptions import BackendConnectionError, SkySnoopError, UnsupportedOperationError

# Unified response model
from skysnoop.models.skydata import SkyData

__all__ = [
    # Primary interface
    "SkySnoop",
    "SkyData",
    # Exceptions
    "SkySnoopError",
    "UnsupportedOperationError",
    "BackendConnectionError",
    # Legacy clients
    "ReAPIClient",
    "OpenAPIClient",
    # Version
    "__version__",
]
