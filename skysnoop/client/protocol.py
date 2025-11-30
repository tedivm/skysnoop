"""Protocol defining the interface contract for backend adapters.

This module defines the BackendProtocol that all backend adapters must implement
to provide a consistent interface for the SkySnoop unified client.

Architecture:
    The adapter pattern is used to provide a unified interface to multiple backends:

    - BackendProtocol: Defines the contract (this module)
    - ReAPIAdapter: Implements protocol for RE-API backend
    - OpenAPIAdapter: Implements protocol for OpenAPI backend
    - SkySnoop: Uses any BackendProtocol implementation

    This design allows adding new backends without changing the SkySnoop client,
    and ensures type safety through Protocol-based structural subtyping.

Design Decisions:
    - All methods return SkyData (not backend-specific response types)
    - Adapters handle normalization from native responses to SkyData
    - Context manager protocol for proper resource management
    - QueryFilters for consistent filtering across backends
    - Simulated operations marked with simulated=True in SkyData
"""

from typing import Protocol

from skysnoop.models.skydata import SkyData
from skysnoop.query.filters import QueryFilters


class BackendProtocol(Protocol):
    """Protocol defining the interface all backend adapters must implement.

    This protocol specifies the contract that backend adapters (OpenAPIAdapter,
    ReAPIAdapter) must fulfill to be compatible with the SkySnoop unified client.
    It ensures type safety and consistent behavior across all backends.

    All methods are async and return SkyData instances. Backends must normalize
    their native response types (APIResponse, V2ResponseModel) into SkyData.

    Example:
        class MyCustomAdapter:
            '''Custom adapter implementing BackendProtocol.'''

            async def get_by_hex(self, hex_code: str) -> SkyData:
                # Implementation that returns SkyData
                ...

            async def __aenter__(self) -> "MyCustomAdapter":
                # Initialize resources
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
                # Cleanup resources
                ...
    """

    async def get_by_hex(self, hex_code: str) -> SkyData:
        """Get aircraft by ICAO hex code.

        Args:
            hex_code: ICAO 24-bit aircraft address (e.g., "abc123")

        Returns:
            SkyData with matching aircraft

        Raises:
            APIError: If the request fails
            ValidationError: If hex_code is invalid
        """
        ...

    async def get_by_callsign(self, callsign: str) -> SkyData:
        """Get aircraft by callsign.

        Args:
            callsign: Aircraft callsign/flight number (e.g., "UAL123")

        Returns:
            SkyData with matching aircraft

        Raises:
            APIError: If the request fails
            ValidationError: If callsign is invalid
        """
        ...

    async def get_by_registration(self, registration: str) -> SkyData:
        """Get aircraft by registration.

        Args:
            registration: Aircraft registration (e.g., "N12345")

        Returns:
            SkyData with matching aircraft

        Raises:
            APIError: If the request fails
            ValidationError: If registration is invalid
        """
        ...

    async def get_by_type(self, aircraft_type: str) -> SkyData:
        """Get aircraft by type designator.

        Args:
            aircraft_type: Aircraft type designator (e.g., "B738", "A320")

        Returns:
            SkyData with matching aircraft

        Raises:
            APIError: If the request fails
            ValidationError: If aircraft_type is invalid
        """
        ...

    async def get_in_circle(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within a circular area.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Search radius in nautical miles
            filters: Optional query filters

        Returns:
            SkyData with aircraft found in the area

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates or radius are invalid
        """
        ...

    async def get_closest(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Find the closest aircraft to a point.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Maximum search radius in nautical miles
            filters: Optional query filters

        Returns:
            SkyData with the closest aircraft (or empty if none found)

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates or radius are invalid
        """
        ...

    async def get_in_box(
        self,
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within a rectangular bounding box.

        Note: Some backends may simulate this operation using a circular query
        with client-side filtering. Check the `simulated` field in the response.

        Args:
            lat_south: Southern latitude boundary in decimal degrees
            lat_north: Northern latitude boundary in decimal degrees
            lon_west: Western longitude boundary in decimal degrees
            lon_east: Eastern longitude boundary in decimal degrees
            filters: Optional query filters

        Returns:
            SkyData with aircraft found in the box area

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates are invalid
        """
        ...

    async def get_all_with_pos(self, filters: QueryFilters | None = None) -> SkyData:
        """Get all aircraft with position data.

        Note: This operation may not be supported by all backends due to
        radius limitations. Backends should raise UnsupportedOperationError
        if they cannot fulfill this request.

        Args:
            filters: Optional query filters

        Returns:
            SkyData with all aircraft that have position data

        Raises:
            UnsupportedOperationError: If the backend cannot support this operation
            APIError: If the request fails
        """
        ...

    async def __aenter__(self) -> "BackendProtocol":
        """Enter async context manager.

        Returns:
            Self for use in async with statements
        """
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        ...
