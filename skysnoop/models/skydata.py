"""Unified response data model for SkySnoop queries.

This module defines the SkyData model that normalizes responses across
different backend APIs (OpenAPI and RE-API) into a consistent interface.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .aircraft import Aircraft


class SkyData(BaseModel):
    """Response data model from SkySnoop queries across all backend types.

    This model provides a unified interface for aircraft data regardless of
    which backend API (OpenAPI or RE-API) was used to retrieve it. It normalizes
    the differences between APIResponse and V2ResponseModel into a consistent
    structure.

    Attributes:
        timestamp: Server timestamp in seconds since epoch (normalized from 'now')
        result_count: Number of aircraft in the response (normalized from 'resultCount'/'total')
        processing_time: Processing time in milliseconds (from RE-API 'ptime', None for OpenAPI)
        aircraft: List of Aircraft objects in the response
        backend: Which backend provided this response ('openapi' or 'reapi')
        simulated: Whether this operation was simulated (e.g., box query via OpenAPI)

    Example:
        >>> async with SkySnoop(backend="auto") as client:
        ...     response = await client.get_by_hex("abc123")
        ...     print(f"Found {response.count} aircraft from {response.backend}")
        ...     for aircraft in response:
        ...         print(f"{aircraft.hex}: {aircraft.callsign}")
    """

    model_config = ConfigDict(
        extra="allow",  # Forward compatibility - allow unknown fields
        populate_by_name=True,
    )

    timestamp: float = Field(..., description="Server timestamp in seconds since epoch")
    result_count: int = Field(..., description="Number of aircraft in the response")
    processing_time: float | None = Field(None, description="Processing time in milliseconds (RE-API only)")
    aircraft: list[Aircraft] = Field(default_factory=list, description="List of aircraft")
    backend: Literal["openapi", "reapi"] = Field(..., description="Backend that provided this response")
    simulated: bool = Field(False, description="Whether this operation was simulated client-side")

    @property
    def count(self) -> int:
        """Get the number of aircraft in the response.

        Returns:
            The number of aircraft returned by the query.

        Example:
            >>> if response.count > 0:
            ...     print(f"Found {response.count} aircraft")
        """
        return self.result_count

    @property
    def has_results(self) -> bool:
        """Check if the response contains any aircraft.

        Returns:
            True if the response contains one or more aircraft, False otherwise.

        Example:
            >>> if response.has_results:
            ...     print("Found aircraft!")
        """
        return self.result_count > 0

    def __len__(self) -> int:
        """Return the number of aircraft in the response.

        Returns:
            The number of aircraft.

        Example:
            >>> response = await client.get_by_hex("abc123")
            >>> print(f"Response contains {len(response)} aircraft")
        """
        return len(self.aircraft)

    def __iter__(self):
        """Iterate over aircraft in the response.

        Yields:
            Aircraft objects from the response.

        Example:
            >>> for aircraft in response:
            ...     print(f"{aircraft.hex}: {aircraft.callsign}")
        """
        return iter(self.aircraft)

    def __str__(self) -> str:
        """Return a human-readable string representation.

        Returns:
            A string describing the response with backend and aircraft count.

        Example:
            >>> print(response)
            SkyData from reapi backend with 5 aircraft
        """
        simulated_note = " (simulated)" if self.simulated else ""
        ptime_info = f" (processed in {self.processing_time}ms)" if self.processing_time is not None else ""
        return f"SkyData from {self.backend} backend with {self.result_count} aircraft{simulated_note}{ptime_info}"
