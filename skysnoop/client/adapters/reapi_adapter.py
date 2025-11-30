"""RE-API adapter implementing BackendProtocol.

This module provides an adapter that wraps ReAPIClient to conform to
the BackendProtocol interface for use with the unified SkySnoop client.

Implementation Details:
    - Wraps ReAPIClient for feeder-only API access
    - Converts APIResponse to SkyData with simulated=False
    - Native support for all operations (no simulation needed)
    - Requires feeder access (must run from feeder IP)
    - Full QueryFilters support with backend-native filtering

Trade-offs:
    - Advantages: Native operations, full filter support, no simulation
    - Disadvantages: Feeder-only access, not publicly accessible
    - Use when: You have feeder access and need full feature support
"""

from logging import getLogger

from skysnoop.client.api import ReAPIClient
from skysnoop.models import SkyData
from skysnoop.models.response import APIResponse
from skysnoop.query.filters import QueryFilters

logger = getLogger(__name__)


class ReAPIAdapter:
    """Adapter for ReAPIClient to BackendProtocol.

    Wraps the ReAPIClient to provide a consistent interface that conforms
    to BackendProtocol. Handles conversion from APIResponse to SkyData
    and provides native support for all operations.

    Example:
        async with ReAPIAdapter() as adapter:
            response = await adapter.get_by_hex("abc123")
            print(f"Found {response.count} aircraft")
    """

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        """Initialize ReAPIAdapter.

        Args:
            base_url: Base URL for the RE-API (default: "https://re-api.adsb.lol")
            timeout: Request timeout in seconds (default: 30.0)
        """
        if base_url is None:
            base_url = "https://re-api.adsb.lol"
        self._client = ReAPIClient(base_url=base_url, timeout=timeout)
        logger.debug(f"ReAPIAdapter initialized with base_url={base_url}")
        """Initialize ReAPIAdapter.

        Args:
            base_url: Base URL for the RE-API (default: "https://re-api.adsb.lol/")
            timeout: Request timeout in seconds (default: 30.0)
        """
        self._client = ReAPIClient(base_url=base_url, timeout=timeout)
        logger.debug(f"ReAPIAdapter initialized with base_url={base_url}")

    async def __aenter__(self) -> "ReAPIAdapter":
        """Enter async context manager."""
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def _convert_api_response(self, api_response: APIResponse, simulated: bool = False) -> SkyData:
        """Convert APIResponse to SkyData.

        Args:
            api_response: Response from RE-API endpoint
            simulated: Whether this operation was simulated (always False for RE-API)

        Returns:
            SkyData instance with normalized fields
        """
        return SkyData(
            timestamp=api_response.now,
            result_count=api_response.resultCount,
            processing_time=api_response.ptime,
            aircraft=api_response.aircraft,  # Already Aircraft instances
            backend="reapi",
            simulated=simulated,
        )

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
        api_response = await self._client.find_hex(hex_code)
        return self._convert_api_response(api_response)

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
        api_response = await self._client.find_callsign(callsign)
        return self._convert_api_response(api_response)

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
        api_response = await self._client.find_reg(registration)
        return self._convert_api_response(api_response)

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
        api_response = await self._client.find_type(aircraft_type)
        return self._convert_api_response(api_response)

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
        api_response = await self._client.circle(lat=lat, lon=lon, radius=radius, filters=filters)
        return self._convert_api_response(api_response)

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
        api_response = await self._client.closest(lat=lat, lon=lon, radius=radius, filters=filters)
        return self._convert_api_response(api_response)

    async def get_in_box(
        self,
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within a rectangular bounding box.

        RE-API has native support for box queries, so this operation is not simulated.

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
        api_response = await self._client.box(
            lat_south=lat_south,
            lat_north=lat_north,
            lon_west=lon_west,
            lon_east=lon_east,
            filters=filters,
        )
        return self._convert_api_response(api_response)

    async def get_all_with_pos(self, filters: QueryFilters | None = None) -> SkyData:
        """Get all aircraft with position data.

        RE-API has native support for retrieving all aircraft with position data.

        Args:
            filters: Optional query filters

        Returns:
            SkyData with all aircraft that have position data

        Raises:
            APIError: If the request fails
        """
        api_response = await self._client.all_with_pos(filters=filters)
        return self._convert_api_response(api_response)
