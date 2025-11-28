"""API response model for adsb.lol API responses.

This module defines the APIResponse model that wraps aircraft data
with metadata from the adsb.lol API.
"""

from pydantic import BaseModel, ConfigDict, Field

from .aircraft import Aircraft


class APIResponse(BaseModel):
    """Represents a complete response from the adsb.lol API.

    This model wraps the list of aircraft with metadata about the query,
    including server timestamp, result count, and processing time.

    Attributes:
        now: Server timestamp in seconds since epoch
        resultCount: Number of aircraft in the response
        ptime: Processing time on the server in milliseconds
        aircraft: List of Aircraft objects in the response
    """

    model_config = ConfigDict(
        extra="allow",  # Forward compatibility - allow unknown fields
        populate_by_name=True,
    )

    now: float = Field(..., description="Server timestamp in seconds since epoch")
    resultCount: int = Field(..., description="Number of aircraft in the response", alias="resultCount")
    ptime: float = Field(..., description="Processing time in milliseconds")
    aircraft: list[Aircraft] = Field(default_factory=list, description="List of aircraft")

    @property
    def count(self) -> int:
        """Get the number of aircraft in the response.

        Returns:
            The number of aircraft returned by the query.
        """
        return self.resultCount

    @property
    def has_results(self) -> bool:
        """Check if the response contains any aircraft.

        Returns:
            True if the response contains one or more aircraft, False otherwise.
        """
        return self.resultCount > 0

    def __len__(self) -> int:
        """Return the number of aircraft in the response.

        Returns:
            The number of aircraft.
        """
        return len(self.aircraft)

    def __iter__(self):
        """Iterate over aircraft in the response.

        Yields:
            Aircraft objects from the response.
        """
        return iter(self.aircraft)

    def __str__(self) -> str:
        """Return a human-readable string representation.

        Returns:
            A string describing the number of aircraft in the response.
        """
        return f"APIResponse with {self.resultCount} aircraft (processed in {self.ptime}ms)"
