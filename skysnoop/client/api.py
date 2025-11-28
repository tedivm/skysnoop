"""High-level API client for adsb.lol.

This module provides the ReAPIClient class that offers a convenient
interface for querying aircraft data from the adsb.lol API.
"""

from logging import getLogger

from skysnoop.client.base import BaseHTTPClient
from skysnoop.models.response import APIResponse
from skysnoop.query.builder import QueryBuilder
from skysnoop.query.filters import QueryFilters

logger = getLogger(__name__)


class ReAPIClient:
    """High-level client for adsb.lol API.

    Provides convenient methods for all query types supported by the API.
    Automatically builds queries, makes HTTP requests, and parses responses
    into typed models.

    Example:
        async with ReAPIClient() as client:
            # Search for aircraft near San Francisco
            response = await client.circle(lat=37.7749, lon=-122.4194, radius=200)
            print(f"Found {response.count} aircraft")

            for aircraft in response:
                if aircraft.has_position:
                    print(f"{aircraft.hex}: {aircraft.callsign}")
    """

    def __init__(self, base_url: str = "https://re-api.adsb.lol/", timeout: float = 30.0):
        """Initialize the API client.

        Args:
            base_url: Base URL for the API (default: "https://re-api.adsb.lol/")
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url
        self.timeout = timeout
        self._http_client: BaseHTTPClient | None = None

    async def __aenter__(self) -> "ReAPIClient":
        """Enter async context manager."""
        self._http_client = BaseHTTPClient(base_url=self.base_url, timeout=self.timeout)
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        if self._http_client:
            await self._http_client.__aexit__(exc_type, exc_val, exc_tb)
            self._http_client = None

    def _ensure_client(self) -> BaseHTTPClient:
        """Ensure HTTP client is initialized."""
        if not self._http_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._http_client

    async def circle(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> APIResponse:
        """Search for aircraft within a circular area.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Search radius in nautical miles
            filters: Optional query filters

        Returns:
            APIResponse with aircraft found in the area

        Example:
            response = await client.circle(lat=37.7749, lon=-122.4194, radius=200)
        """
        client = self._ensure_client()
        query = QueryBuilder.build_circle(lat=lat, lon=lon, radius=radius, filters=filters)
        logger.debug(f"Circle query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def closest(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> APIResponse:
        """Find the closest aircraft to a point.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Search radius in nautical miles
            filters: Optional query filters

        Returns:
            APIResponse with at most one aircraft (the closest)

        Example:
            response = await client.closest(lat=37.7749, lon=-122.4194, radius=500)
        """
        client = self._ensure_client()
        query = QueryBuilder.build_closest(lat=lat, lon=lon, radius=radius, filters=filters)
        logger.debug(f"Closest query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def box(
        self,
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
        filters: QueryFilters | None = None,
    ) -> APIResponse:
        """Search for aircraft within a bounding box.

        Args:
            lat_south: Southern latitude boundary in decimal degrees
            lat_north: Northern latitude boundary in decimal degrees
            lon_west: Western longitude boundary in decimal degrees
            lon_east: Eastern longitude boundary in decimal degrees
            filters: Optional query filters

        Returns:
            APIResponse with aircraft found in the box

        Example:
            response = await client.box(
                lat_south=37.0,
                lat_north=38.5,
                lon_west=-123.0,
                lon_east=-121.0,
            )
        """
        client = self._ensure_client()
        query = QueryBuilder.build_box(
            lat_south=lat_south,
            lat_north=lat_north,
            lon_west=lon_west,
            lon_east=lon_east,
            filters=filters,
        )
        logger.debug(f"Box query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def find_hex(self, hex_code: str) -> APIResponse:
        """Find aircraft by ICAO hex code.

        Args:
            hex_code: ICAO 24-bit aircraft address (hex)

        Returns:
            APIResponse with matching aircraft

        Example:
            response = await client.find_hex("a12345")
        """
        client = self._ensure_client()
        query = QueryBuilder.build_find_hex(hex_code)
        logger.debug(f"Find hex query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def find_callsign(self, callsign: str) -> APIResponse:
        """Find aircraft by callsign.

        Args:
            callsign: Aircraft callsign/flight number

        Returns:
            APIResponse with matching aircraft

        Example:
            response = await client.find_callsign("UAL123")
        """
        client = self._ensure_client()
        query = QueryBuilder.build_find_callsign(callsign)
        logger.debug(f"Find callsign query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def find_reg(self, registration: str) -> APIResponse:
        """Find aircraft by registration.

        Args:
            registration: Aircraft registration number

        Returns:
            APIResponse with matching aircraft

        Example:
            response = await client.find_reg("N12345")
        """
        client = self._ensure_client()
        query = QueryBuilder.build_find_reg(registration)
        logger.debug(f"Find registration query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def find_type(self, type_code: str) -> APIResponse:
        """Find aircraft by type code.

        Args:
            type_code: Aircraft type code (e.g., "A321", "B738")

        Returns:
            APIResponse with matching aircraft

        Example:
            response = await client.find_type("A321")
        """
        client = self._ensure_client()
        query = QueryBuilder.build_find_type(type_code)
        logger.debug(f"Find type query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def all_with_pos(self, filters: QueryFilters | None = None) -> APIResponse:
        """Get all aircraft with position data.

        Args:
            filters: Optional query filters

        Returns:
            APIResponse with all aircraft that have position data

        Example:
            response = await client.all_with_pos()
        """
        client = self._ensure_client()
        query = QueryBuilder.build_all_with_pos(filters=filters)
        logger.debug(f"All with pos query: {query}")

        data = await client.get(query)
        return APIResponse(**data)

    async def all(self, filters: QueryFilters | None = None) -> APIResponse:
        """Get all aircraft.

        Args:
            filters: Optional query filters

        Returns:
            APIResponse with all aircraft

        Example:
            response = await client.all()
        """
        client = self._ensure_client()
        query = QueryBuilder.build_all(filters=filters)
        logger.debug(f"All query: {query}")

        data = await client.get(query)
        return APIResponse(**data)
