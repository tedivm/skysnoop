"""SkySnoop unified client - primary interface for adsb.lol API access.

This module provides the SkySnoop class, which is the main entry point for using
the library. It provides a consistent interface that works with both OpenAPI and
RE-API backends, automatically handling differences and providing unified responses.
"""

import logging
from typing import Literal

from skysnoop.client.adapters.openapi_adapter import OpenAPIAdapter
from skysnoop.client.adapters.reapi_adapter import ReAPIAdapter
from skysnoop.client.backend_selection import select_backend_sync
from skysnoop.client.protocol import BackendProtocol
from skysnoop.models.skydata import SkyData
from skysnoop.query.filters import QueryFilters

logger = logging.getLogger(__name__)


class SkySnoop:
    """Unified client for adsb.lol API access.

    SkySnoop provides a consistent interface for querying aircraft data from adsb.lol,
    automatically selecting and managing the appropriate backend (OpenAPI or RE-API).
    All methods return SkyData objects with normalized aircraft information.

    The client supports automatic backend selection based on configuration, or explicit
    backend selection when needed. RE-API is preferred by default as the stable backend
    with full feature support, but OpenAPI is used when an API key is provided (for
    future compatibility) or as a fallback.

    Examples:
        >>> # Auto-select backend (recommended - uses RE-API by default)
        >>> async with SkySnoop() as client:
        ...     result = await client.get_by_hex("abc123")
        ...     print(f"Found {result.count} aircraft")
        >>>
        >>> # Explicitly use RE-API backend
        >>> async with SkySnoop(backend="reapi") as client:
        ...     result = await client.get_in_box(
        ...         lat_min=37.0, lat_max=38.0,
        ...         lon_min=-123.0, lon_max=-122.0
        ...     )
        >>>
        >>> # Use OpenAPI backend with filters (filters ignored with warning)
        >>> async with SkySnoop(backend="openapi") as client:
        ...     filters = QueryFilters(military=True)
        ...     result = await client.get_in_circle(37.7749, -122.4194, 50, filters=filters)
        >>>
        >>> # Provide API key (triggers OpenAPI backend)
        >>> async with SkySnoop(api_key="future_key") as client:
        ...     result = await client.get_by_callsign("UAL123")

    Attributes:
        backend_type: The backend type being used ("openapi" or "reapi")
        _adapter: The backend adapter instance (OpenAPIAdapter or ReAPIAdapter)
        _api_key: Optional API key for OpenAPI backend
        _base_url: Optional custom base URL for backend
        _timeout: Request timeout in seconds
    """

    def __init__(
        self,
        backend: Literal["auto", "openapi", "reapi"] = "auto",
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize SkySnoop client with backend selection.

        Args:
            backend: Backend selection - "auto" (recommended), "openapi", or "reapi"
                    "auto" selects RE-API by default, OpenAPI if API key provided
            api_key: Optional API key for OpenAPI backend (triggers OpenAPI selection)
            base_url: Optional custom base URL for the backend
            timeout: Request timeout in seconds (default 30.0)

        Examples:
            >>> # Auto-select (uses RE-API by default)
            >>> client = SkySnoop()
            >>>
            >>> # Explicit RE-API backend
            >>> client = SkySnoop(backend="reapi")
            >>>
            >>> # Explicit OpenAPI backend
            >>> client = SkySnoop(backend="openapi")
            >>>
            >>> # API key triggers OpenAPI
            >>> client = SkySnoop(api_key="future_key")
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._adapter: BackendProtocol | None = None

        # Select backend
        if backend == "auto":
            self.backend_type = select_backend_sync(api_key=api_key, prefer_reapi=True)
            logger.info(f"Auto-selected backend: {self.backend_type}")
        elif backend in ("openapi", "reapi"):
            self.backend_type = backend
            logger.info(f"Explicitly selected backend: {self.backend_type}")
        else:
            raise ValueError(f"Invalid backend: {backend}. Must be 'auto', 'openapi', or 'reapi'")

    async def __aenter__(self) -> "SkySnoop":
        """Async context manager entry - initialize backend adapter."""
        # Instantiate appropriate adapter
        if self.backend_type == "openapi":
            logger.debug("Initializing OpenAPIAdapter")
            self._adapter = OpenAPIAdapter(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout,
            )
        else:  # reapi
            logger.debug("Initializing ReAPIAdapter")
            self._adapter = ReAPIAdapter(
                base_url=self._base_url,
                timeout=self._timeout,
            )

        # Enter adapter context
        await self._adapter.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup backend adapter."""
        if self._adapter:
            await self._adapter.__aexit__(exc_type, exc_val, exc_tb)
            self._adapter = None

    def _ensure_adapter(self) -> BackendProtocol:
        """Ensure adapter is initialized, raise error if not."""
        if self._adapter is None:
            raise RuntimeError("SkySnoop must be used as an async context manager")
        return self._adapter

    async def get_by_hex(self, hex_code: str) -> SkyData:
        """Get aircraft by ICAO hex code.

        Args:
            hex_code: ICAO 24-bit hex identifier (e.g., "abc123")

        Returns:
            SkyData with matching aircraft (may be empty if not found)

        Examples:
            >>> async with SkySnoop() as client:
            ...     result = await client.get_by_hex("abc123")
            ...     if result.has_results:
            ...         aircraft = result.aircraft[0]
            ...         print(f"{aircraft.registration} - {aircraft.type}")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_by_hex(hex_code=hex_code)

    async def get_by_callsign(self, callsign: str) -> SkyData:
        """Get aircraft by callsign/flight number.

        Args:
            callsign: Aircraft callsign or flight number (e.g., "UAL123")

        Returns:
            SkyData with matching aircraft (may contain multiple results)

        Examples:
            >>> async with SkySnoop() as client:
            ...     result = await client.get_by_callsign("UAL123")
            ...     for aircraft in result:
            ...         print(f"{aircraft.hex} - {aircraft.callsign}")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_by_callsign(callsign=callsign)

    async def get_by_registration(self, registration: str) -> SkyData:
        """Get aircraft by registration number.

        Args:
            registration: Aircraft registration (e.g., "N12345")

        Returns:
            SkyData with matching aircraft (may be empty if not found)

        Examples:
            >>> async with SkySnoop() as client:
            ...     result = await client.get_by_registration("N12345")
            ...     if result.has_results:
            ...         print(f"Found: {result.aircraft[0].type}")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_by_registration(registration=registration)

    async def get_by_type(self, aircraft_type: str) -> SkyData:
        """Get aircraft by type code.

        Args:
            aircraft_type: Aircraft type code (e.g., "B738", "A321")

        Returns:
            SkyData with matching aircraft (may contain multiple results)

        Examples:
            >>> async with SkySnoop() as client:
            ...     result = await client.get_by_type("B738")
            ...     print(f"Found {result.count} Boeing 737-800 aircraft")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_by_type(aircraft_type=aircraft_type)

    async def get_in_circle(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within circular area.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Radius in nautical miles
            filters: Optional query filters (RE-API only, ignored with warning on OpenAPI)

        Returns:
            SkyData with aircraft in circular area

        Examples:
            >>> async with SkySnoop() as client:
            ...     # San Francisco area, 50 NM radius
            ...     result = await client.get_in_circle(37.7749, -122.4194, 50)
            ...     print(f"Found {result.count} aircraft nearby")
            >>>
            >>> # With filters (RE-API only)
            >>> async with SkySnoop(backend="reapi") as client:
            ...     filters = QueryFilters(military=True)
            ...     result = await client.get_in_circle(37.7749, -122.4194, 50, filters=filters)
        """
        adapter = self._ensure_adapter()
        return await adapter.get_in_circle(lat=lat, lon=lon, radius=radius, filters=filters)

    async def get_closest(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get closest aircraft to a point within search radius.

        Args:
            lat: Reference latitude in decimal degrees
            lon: Reference longitude in decimal degrees
            radius: Maximum search radius in nautical miles
            filters: Optional query filters (RE-API only, ignored with warning on OpenAPI)

        Returns:
            SkyData with closest aircraft (may be empty if none within radius)

        Examples:
            >>> async with SkySnoop() as client:
            ...     result = await client.get_closest(37.7749, -122.4194, 100)
            ...     if result.has_results:
            ...         aircraft = result.aircraft[0]
            ...         print(f"Closest: {aircraft.callsign} at {aircraft.alt_baro}ft")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_closest(lat=lat, lon=lon, radius=radius, filters=filters)

    async def get_in_box(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within rectangular bounding box.

        Note: OpenAPI backend simulates box queries using circular area + client-side
        filtering. The SkyData.simulated flag indicates simulation. RE-API backend
        provides native box query support.

        Args:
            lat_min: Minimum latitude in decimal degrees
            lat_max: Maximum latitude in decimal degrees
            lon_min: Minimum longitude in decimal degrees
            lon_max: Maximum longitude in decimal degrees
            filters: Optional query filters (RE-API only, ignored with warning on OpenAPI)

        Returns:
            SkyData with aircraft in bounding box (simulated=True for OpenAPI)

        Examples:
            >>> async with SkySnoop() as client:
            ...     # Bay Area box
            ...     result = await client.get_in_box(
            ...         lat_min=37.0, lat_max=38.0,
            ...         lon_min=-123.0, lon_max=-122.0
            ...     )
            ...     if result.simulated:
            ...         print("Note: Box query simulated via OpenAPI backend")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_in_box(
            lat_south=lat_min,
            lat_north=lat_max,
            lon_west=lon_min,
            lon_east=lon_max,
            filters=filters,
        )

    async def get_all_with_pos(self, filters: QueryFilters | None = None) -> SkyData:
        """Get all aircraft with position data.

        Note: OpenAPI backend raises UnsupportedOperationError (250 NM limit prevents
        global queries). RE-API backend provides native support for this operation.
        Use RE-API backend when this operation is needed.

        Args:
            filters: Optional query filters (RE-API only)

        Returns:
            SkyData with all aircraft having position data (RE-API only)

        Raises:
            UnsupportedOperationError: When using OpenAPI backend (not supported)

        Examples:
            >>> # Must use RE-API backend
            >>> async with SkySnoop(backend="reapi") as client:
            ...     filters = QueryFilters(military=True)
            ...     result = await client.get_all_with_pos(filters=filters)
            ...     print(f"Found {result.count} military aircraft worldwide")
        """
        adapter = self._ensure_adapter()
        return await adapter.get_all_with_pos(filters=filters)
