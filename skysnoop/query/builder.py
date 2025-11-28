"""Query builder for constructing adsb.lol API query strings.

This module provides the QueryBuilder class for constructing properly formatted
query strings for the adsb.lol API. Query strings are returned as strings (NOT dicts)
to avoid httpx URL-encoding commas, which would break the API.
"""

from skysnoop.query.filters import QueryFilters


class QueryBuilder:
    """Constructs query strings for adsb.lol API queries.

    All methods return properly formatted query strings that preserve commas
    in coordinate and parameter values. Do NOT use httpx params dict as it
    will URL-encode commas and break the API.
    """

    @staticmethod
    def build_circle(
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> str:
        """Build query string for circular area search.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius: Radius in nautical miles
            filters: Optional query filters

        Returns:
            Query string like "circle=lat,lon,radius&filter1=value1"
        """
        query = f"circle={lat},{lon},{radius}"
        if filters:
            filter_str = filters.to_query_string()
            if filter_str:
                query = f"{query}&{filter_str}"
        return query

    @staticmethod
    def build_closest(
        lat: float,
        lon: float,
        radius: float,
        filters: QueryFilters | None = None,
    ) -> str:
        """Build query string for finding closest aircraft.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius: Search radius in nautical miles
            filters: Optional query filters

        Returns:
            Query string like "closest=lat,lon,radius&filter1=value1"
        """
        query = f"closest={lat},{lon},{radius}"
        if filters:
            filter_str = filters.to_query_string()
            if filter_str:
                query = f"{query}&{filter_str}"
        return query

    @staticmethod
    def build_box(
        lat_south: float,
        lat_north: float,
        lon_west: float,
        lon_east: float,
        filters: QueryFilters | None = None,
    ) -> str:
        """Build query string for bounding box search.

        Args:
            lat_south: Southern latitude boundary in decimal degrees
            lat_north: Northern latitude boundary in decimal degrees
            lon_west: Western longitude boundary in decimal degrees
            lon_east: Eastern longitude boundary in decimal degrees
            filters: Optional query filters

        Returns:
            Query string like "box=lat_south,lat_north,lon_west,lon_east&filter1=value1"
        """
        query = f"box={lat_south},{lat_north},{lon_west},{lon_east}"
        if filters:
            filter_str = filters.to_query_string()
            if filter_str:
                query = f"{query}&{filter_str}"
        return query

    @staticmethod
    def build_find_hex(hex_code: str) -> str:
        """Build query string for finding aircraft by ICAO hex code.

        Args:
            hex_code: ICAO 24-bit aircraft address (hex)

        Returns:
            Query string like "find_hex=abc123"
        """
        return f"find_hex={hex_code}"

    @staticmethod
    def build_find_callsign(callsign: str) -> str:
        """Build query string for finding aircraft by callsign.

        Args:
            callsign: Aircraft callsign/flight number

        Returns:
            Query string like "find_callsign=UAL123"
        """
        return f"find_callsign={callsign}"

    @staticmethod
    def build_find_reg(registration: str) -> str:
        """Build query string for finding aircraft by registration.

        Args:
            registration: Aircraft registration number

        Returns:
            Query string like "find_reg=N12345"
        """
        return f"find_reg={registration}"

    @staticmethod
    def build_find_type(type_code: str) -> str:
        """Build query string for finding aircraft by type code.

        Args:
            type_code: Aircraft type code (e.g., "A321", "B738")

        Returns:
            Query string like "find_type=A321"
        """
        return f"find_type={type_code}"

    @staticmethod
    def build_all(filters: QueryFilters | None = None) -> str:
        """Build query string for getting all aircraft.

        Args:
            filters: Optional query filters

        Returns:
            Query string like "all&filter1=value1" or just "all"
        """
        query = "all"
        if filters:
            filter_str = filters.to_query_string()
            if filter_str:
                query = f"{query}&{filter_str}"
        return query

    @staticmethod
    def build_all_with_pos(filters: QueryFilters | None = None) -> str:
        """Build query string for getting all aircraft with positions.

        Args:
            filters: Optional query filters

        Returns:
            Query string like "all_with_pos&filter1=value1" or just "all_with_pos"
        """
        query = "all_with_pos"
        if filters:
            filter_str = filters.to_query_string()
            if filter_str:
                query = f"{query}&{filter_str}"
        return query
