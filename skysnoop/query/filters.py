"""Query filter definitions for adsb.lol API.

This module defines the QueryFilters class for specifying filter criteria
that can be applied to API queries.
"""

from urllib.parse import urlencode

from pydantic import BaseModel, Field, model_validator


class QueryFilters(BaseModel):
    """Filter criteria for adsb.lol API queries.

    All fields are optional. Filters can be combined unless mutually exclusive.

    Attributes:
        callsign_exact: Exact callsign match (mutually exclusive with callsign_prefix)
        callsign_prefix: Callsign prefix match (mutually exclusive with callsign_exact)
        squawk: Squawk code filter
        type_code: Aircraft type code filter (e.g., "A321", "B738")
        above_alt_baro: Minimum barometric altitude in feet
        below_alt_baro: Maximum barometric altitude in feet
        mil: Filter for military aircraft
        pia: Filter for privacy/PIA flag
        ladd: Filter for LADD flag
    """

    callsign_exact: str | None = Field(None, description="Exact callsign match")
    callsign_prefix: str | None = Field(None, description="Callsign prefix match")
    squawk: str | None = Field(None, description="Squawk code filter")
    type_code: str | None = Field(None, description="Aircraft type code")
    above_alt_baro: int | None = Field(None, description="Minimum barometric altitude in feet")
    below_alt_baro: int | None = Field(None, description="Maximum barometric altitude in feet")
    mil: bool | None = Field(None, description="Filter for military aircraft")
    pia: bool | None = Field(None, description="Filter for privacy/PIA flag")
    ladd: bool | None = Field(None, description="Filter for LADD flag")

    @model_validator(mode="after")
    def validate_callsign_filters(self) -> "QueryFilters":
        """Validate that callsign_exact and callsign_prefix are mutually exclusive."""
        if self.callsign_exact is not None and self.callsign_prefix is not None:
            raise ValueError("callsign_exact and callsign_prefix are mutually exclusive")
        return self

    @model_validator(mode="after")
    def validate_altitude_range(self) -> "QueryFilters":
        """Validate that altitude range is valid."""
        if (
            self.above_alt_baro is not None
            and self.below_alt_baro is not None
            and self.above_alt_baro > self.below_alt_baro
        ):
            raise ValueError(
                f"above_alt_baro ({self.above_alt_baro}) must be less than below_alt_baro ({self.below_alt_baro})"
            )
        return self

    def to_query_params(self) -> dict[str, str]:
        """Convert filters to URL query parameters.

        Returns:
            Dictionary of filter parameters with 'filter_' prefix for API.
        """
        params: dict[str, str] = {}

        if self.callsign_exact is not None:
            params["filter_callsign"] = self.callsign_exact
        if self.callsign_prefix is not None:
            params["filter_callsign_prefix"] = self.callsign_prefix
        if self.squawk is not None:
            params["filter_squawk"] = self.squawk
        if self.type_code is not None:
            params["filter_type"] = self.type_code
        if self.above_alt_baro is not None:
            params["filter_above_alt_baro"] = str(self.above_alt_baro)
        if self.below_alt_baro is not None:
            params["filter_below_alt_baro"] = str(self.below_alt_baro)
        if self.mil is not None:
            params["filter_mil"] = "true" if self.mil else "false"
        if self.pia is not None:
            params["filter_pia"] = "true" if self.pia else "false"
        if self.ladd is not None:
            params["filter_ladd"] = "true" if self.ladd else "false"

        return params

    def to_query_string(self) -> str:
        """Convert filters to URL query string.

        Returns:
            URL-encoded query string (without leading '?').
            Empty string if no filters are set.
        """
        params = self.to_query_params()
        if not params:
            return ""
        return urlencode(params)
