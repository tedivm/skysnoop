"""OpenAPI adapter implementing BackendProtocol.

This module provides an adapter that wraps OpenAPIClient to conform to
the BackendProtocol interface for use with the unified SkySnoop client.

Implementation Details:
    - Wraps OpenAPIClient for public API access
    - Converts V2ResponseModel to SkyData with simulated flag
    - Simulates geographic queries (circle, closest, box) by fetching all aircraft
    - Does not support get_all_with_pos() (raises UnsupportedOperationError)
    - Limited QueryFilters support (only military filter via /mil endpoint)
    - API key accepted for future compatibility (not currently required)

Simulation Strategy:
    Geographic queries (circle, closest, box) are simulated by:
    1. Fetching all aircraft with position data
    2. Filtering client-side using geographic calculations
    3. Marking results with simulated=True in SkyData

    This provides functionality at the cost of fetching more data.

Trade-offs:
    - Advantages: Public access, no feeder requirement, future API key support
    - Disadvantages: Simulated operations, limited filters, no bulk queries
    - Use when: You don't have feeder access or need public API compatibility
"""

import math
from logging import getLogger

from skysnoop.client.openapi import OpenAPIClient
from skysnoop.exceptions import UnsupportedOperationError
from skysnoop.models import Aircraft, SkyData
from skysnoop.models.openapi import V2ResponseAcItem, V2ResponseModel
from skysnoop.query.filters import QueryFilters

logger = getLogger(__name__)


class OpenAPIAdapter:
    """Adapter for OpenAPIClient to BackendProtocol.

    Wraps the OpenAPIClient to provide a consistent interface that conforms
    to BackendProtocol. Handles conversion from V2ResponseModel to SkyData
    and provides simulation for operations not natively supported by OpenAPI.

    Note: api_key is accepted for future compatibility but not currently
    required by the OpenAPI.

    Example:
        async with OpenAPIAdapter() as adapter:
            response = await adapter.get_by_hex("abc123")
            print(f"Found {response.count} aircraft")
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize OpenAPIAdapter.

        Args:
            api_key: Optional API key (for future compatibility, not currently required)
            base_url: Base URL for the OpenAPI (default: "https://api.adsb.lol")
            timeout: Request timeout in seconds (default: 30.0)
        """
        if base_url is None:
            base_url = "https://api.adsb.lol"
        self._client = OpenAPIClient(api_key=api_key, base_url=base_url, timeout=timeout)
        logger.debug(f"OpenAPIAdapter initialized with base_url={base_url}")

    async def __aenter__(self) -> "OpenAPIAdapter":
        """Enter async context manager."""
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def _convert_v2_response(self, v2_response: V2ResponseModel, simulated: bool = False) -> SkyData:
        """Convert V2ResponseModel to SkyData.

        Args:
            v2_response: Response from OpenAPI v2 endpoint
            simulated: Whether this operation was simulated client-side

        Returns:
            SkyData instance with normalized fields
        """
        aircraft = [self._convert_aircraft(ac) for ac in v2_response.ac]

        return SkyData(
            timestamp=float(v2_response.now),
            result_count=v2_response.total,
            processing_time=None,  # OpenAPI doesn't provide processing time
            aircraft=aircraft,
            backend="openapi",
            simulated=simulated,
        )

    def _convert_aircraft(self, v2_aircraft: V2ResponseAcItem) -> Aircraft:
        """Convert V2ResponseAcItem to Aircraft.

        Maps OpenAPI aircraft fields to the common Aircraft model. Handles
        field name differences and missing fields gracefully.

        Args:
            v2_aircraft: Aircraft data from OpenAPI v2 response

        Returns:
            Aircraft instance with normalized fields
        """
        # Map OpenAPI field names to Aircraft field names
        # OpenAPI uses 't' for type and 'r' for registration
        return Aircraft(
            hex=v2_aircraft.hex,
            flight=v2_aircraft.flight,
            squawk=v2_aircraft.squawk,
            registration=v2_aircraft.r,  # OpenAPI uses 'r' for registration
            type=v2_aircraft.t,  # OpenAPI uses 't' for type
            category=v2_aircraft.category,
            lat=v2_aircraft.lat,
            lon=v2_aircraft.lon,
            seen_pos=v2_aircraft.seen_pos,
            alt_baro=v2_aircraft.alt_baro,
            alt_geom=v2_aircraft.alt_geom,
            baro_rate=v2_aircraft.baro_rate,
            geom_rate=v2_aircraft.geom_rate,
            gs=v2_aircraft.gs,
            ias=v2_aircraft.ias,
            tas=v2_aircraft.tas,
            mach=v2_aircraft.mach,
            track=v2_aircraft.track,
            track_rate=v2_aircraft.track_rate,
            roll=v2_aircraft.roll,
            mag_heading=v2_aircraft.mag_heading,
            true_heading=v2_aircraft.true_heading,
            nav_qnh=v2_aircraft.nav_qnh,
            nav_altitude_mcp=v2_aircraft.nav_altitude_mcp,
            nav_altitude_fms=v2_aircraft.nav_altitude_fms,
            nav_heading=v2_aircraft.nav_heading,
            nav_modes=v2_aircraft.nav_modes,
            nic=v2_aircraft.nic,
            rc=v2_aircraft.rc,
            version=v2_aircraft.version,
            nic_baro=v2_aircraft.nic_baro,
            nac_p=v2_aircraft.nac_p,
            nac_v=v2_aircraft.nac_v,
            sil=v2_aircraft.sil,
            sil_type=v2_aircraft.sil_type,
            gva=v2_aircraft.gva,
            sda=v2_aircraft.sda,
            alert=v2_aircraft.alert,
            spi=v2_aircraft.spi,
            mlat=v2_aircraft.mlat,
            tisb=v2_aircraft.tisb,
            messages=v2_aircraft.messages,
            seen=v2_aircraft.seen,
            rssi=v2_aircraft.rssi,
            emergency=v2_aircraft.emergency,
            dbFlags=v2_aircraft.db_flags,
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
        v2_response = await self._client.v2.get_by_hex(hex_code)
        return self._convert_v2_response(v2_response)

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
        v2_response = await self._client.v2.get_by_callsign(callsign)
        return self._convert_v2_response(v2_response)

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
        v2_response = await self._client.v2.get_by_registration(registration)
        return self._convert_v2_response(v2_response)

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
        v2_response = await self._client.v2.get_by_type(aircraft_type)
        return self._convert_v2_response(v2_response)

    async def get_in_circle(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within a circular area.

        Note: OpenAPI does not currently support QueryFilters. Filters are ignored.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Search radius in nautical miles
            filters: Optional query filters (currently ignored for OpenAPI)

        Returns:
            SkyData with aircraft found in the area

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates or radius are invalid
        """
        if filters:
            logger.warning("OpenAPI does not support QueryFilters - filters will be ignored")

        v2_response = await self._client.v2.get_by_point(lat=lat, lon=lon, radius=int(radius))
        return self._convert_v2_response(v2_response)

    async def get_closest(
        self,
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Find the closest aircraft to a point.

        Note: OpenAPI does not currently support QueryFilters. Filters are ignored.

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            radius: Maximum search radius in nautical miles
            filters: Optional query filters (currently ignored for OpenAPI)

        Returns:
            SkyData with the closest aircraft (or empty if none found)

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates or radius are invalid
        """
        if filters:
            logger.warning("OpenAPI does not support QueryFilters - filters will be ignored")

        v2_response = await self._client.v2.get_closest(lat=lat, lon=lon, radius=int(radius))
        return self._convert_v2_response(v2_response)

    async def get_in_box(
        self,
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
        filters: QueryFilters | None = None,
    ) -> SkyData:
        """Get aircraft within a rectangular bounding box.

        Note: This operation is simulated using a circular query with client-side
        filtering. OpenAPI does not natively support box queries.

        The implementation:
        1. Calculates a bounding circle that contains the entire box
        2. Fetches all aircraft within that circle
        3. Filters results client-side to only include aircraft within the box

        Args:
            lat_south: Southern latitude boundary in decimal degrees
            lat_north: Northern latitude boundary in decimal degrees
            lon_west: Western longitude boundary in decimal degrees
            lon_east: Eastern longitude boundary in decimal degrees
            filters: Optional query filters (currently ignored for OpenAPI)

        Returns:
            SkyData with aircraft found in the box area (simulated=True)

        Raises:
            APIError: If the request fails
            ValidationError: If coordinates are invalid
        """
        if filters:
            logger.warning("OpenAPI does not support QueryFilters - filters will be ignored")

        logger.debug(f"Simulating box query for OpenAPI: lat=[{lat_south}, {lat_north}], lon=[{lon_west}, {lon_east}]")

        # Calculate center point and radius for bounding circle
        center_lat = (lat_south + lat_north) / 2
        center_lon = (lon_west + lon_east) / 2

        # Calculate radius as distance from center to corner (with some buffer)
        # Using Haversine distance formula for accuracy
        radius = self._calculate_haversine_distance(center_lat, center_lon, lat_north, lon_east) * 1.1  # 10% buffer

        logger.debug(f"Bounding circle: center=({center_lat}, {center_lon}), radius={radius:.2f} NM")

        # Fetch aircraft within bounding circle
        v2_response = await self._client.v2.get_by_point(lat=center_lat, lon=center_lon, radius=int(radius))

        # Filter to box bounds
        filtered_aircraft = []
        for ac in v2_response.ac:
            if self._is_in_box(ac, lat_south, lat_north, lon_west, lon_east):
                filtered_aircraft.append(self._convert_aircraft(ac))

        logger.debug(f"Filtered {v2_response.total} aircraft to {len(filtered_aircraft)} within box")

        return SkyData(
            timestamp=float(v2_response.now),
            result_count=len(filtered_aircraft),
            processing_time=None,
            aircraft=filtered_aircraft,
            backend="openapi",
            simulated=True,
        )

    async def get_all_with_pos(self, filters: QueryFilters | None = None) -> SkyData:
        """Get all aircraft with position data.

        Note: This operation is not supported by OpenAPI due to the 250 NM
        radius limitation. Use the RE-API backend for this operation.

        Args:
            filters: Optional query filters (not applicable)

        Raises:
            UnsupportedOperationError: Always raised - operation not supported
        """
        raise UnsupportedOperationError(
            "get_all_with_pos() is not supported by the OpenAPI backend due to "
            "the 250 NM radius limitation. Please use backend='reapi' for this operation."
        )

    def _calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula.

        Args:
            lat1: First point latitude in decimal degrees
            lon1: First point longitude in decimal degrees
            lat2: Second point latitude in decimal degrees
            lon2: Second point longitude in decimal degrees

        Returns:
            Distance in nautical miles
        """
        # Earth radius in nautical miles
        R = 3440.065

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _is_in_box(
        self,
        aircraft: V2ResponseAcItem,
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
    ) -> bool:
        """Check if aircraft is within box bounds.

        Handles longitude wraparound (e.g., box crossing 180° meridian).

        Args:
            aircraft: Aircraft to check
            lat_south: Southern latitude boundary
            lat_north: Northern latitude boundary
            lon_west: Western longitude boundary
            lon_east: Eastern longitude boundary

        Returns:
            True if aircraft is within box bounds, False otherwise
        """
        # Aircraft must have position data
        if aircraft.lat is None or aircraft.lon is None:
            return False

        # Check latitude (straightforward)
        if not (lat_south <= aircraft.lat <= lat_north):
            return False

        # Check longitude (handle wraparound)
        if lon_west <= lon_east:
            # Normal case: box doesn't cross 180° meridian
            return lon_west <= aircraft.lon <= lon_east
        else:
            # Wraparound case: box crosses 180° meridian
            # Aircraft is in box if it's either west of east bound OR east of west bound
            return aircraft.lon >= lon_west or aircraft.lon <= lon_east
