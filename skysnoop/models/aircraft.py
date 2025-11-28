"""Aircraft data model for adsb.lol API responses.

This module defines the Aircraft model representing a single aircraft's
telemetry data from the adsb.lol API.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Aircraft(BaseModel):
    """Represents a single aircraft with telemetry data from adsb.lol.

    All fields except `hex` are optional as the API may not provide all data
    for every aircraft. The model uses forward-compatible configuration to
    handle future API additions gracefully.

    Attributes:
        hex: ICAO 24-bit aircraft address (required)
        flight: Aircraft callsign/flight number
        alt_baro: Barometric altitude in feet
        alt_geom: Geometric (GNSS/INS) altitude in feet
        gs: Ground speed in knots
        ias: Indicated airspeed in knots
        tas: True airspeed in knots
        mach: Mach number
        track: Track over ground in degrees (0-359)
        track_rate: Rate of change of track in degrees/second
        roll: Roll angle in degrees
        mag_heading: Magnetic heading in degrees
        true_heading: True heading in degrees
        baro_rate: Rate of change of barometric altitude in feet/minute
        geom_rate: Rate of change of geometric altitude in feet/minute
        squawk: Mode A transponder code
        emergency: Emergency/priority status
        category: Aircraft category (e.g., A1, A2)
        nav_qnh: QNH setting in millibars
        nav_altitude_mcp: Selected altitude from MCP/FCU in feet
        nav_altitude_fms: Selected altitude from FMS in feet
        nav_heading: Selected heading in degrees
        nav_modes: Navigation modes (list of strings)
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        nic: Navigation Integrity Category
        rc: Radius of Containment in meters
        seen_pos: Seconds since position last updated
        version: ADS-B version number
        nic_baro: NIC for barometric altitude
        nac_p: Navigation Accuracy Category - Position
        nac_v: Navigation Accuracy Category - Velocity
        sil: Source Integrity Level
        sil_type: SIL supplement type
        gva: Geometric Vertical Accuracy
        sda: System Design Assurance
        alert: Alert flag
        spi: Special Position Indicator flag
        mlat: Position from multilateration (list of strings)
        tisb: Position from TIS-B (list of strings)
        messages: Total number of Mode S messages received
        seen: Seconds since any message last received
        rssi: Signal strength in dBFS
        dst: Distance from receiver in nautical miles
        dir: Direction from receiver in degrees
        flight_status: Flight status description
        type: Aircraft type code
        registration: Aircraft registration
        dbFlags: Database flags
        year: Year of manufacture
    """

    model_config = ConfigDict(
        extra="allow",  # Forward compatibility - allow unknown fields
        populate_by_name=True,
    )

    # Required field
    hex: str = Field(..., description="ICAO 24-bit aircraft address")

    # Identification
    flight: str | None = Field(None, description="Aircraft callsign/flight number")
    squawk: str | None = Field(None, description="Mode A transponder code")
    registration: str | None = Field(None, description="Aircraft registration")
    type: str | None = Field(None, description="Aircraft type code")
    category: str | None = Field(None, description="Aircraft category")

    # Position
    lat: float | None = Field(None, description="Latitude in decimal degrees", ge=-90, le=90)
    lon: float | None = Field(None, description="Longitude in decimal degrees", ge=-180, le=180)
    seen_pos: float | None = Field(None, description="Seconds since position last updated")

    # Altitude (can be int or "ground" for aircraft on the ground)
    alt_baro: int | Literal["ground"] | None = Field(None, description="Barometric altitude in feet or 'ground'")
    alt_geom: int | Literal["ground"] | None = Field(None, description="Geometric altitude in feet or 'ground'")
    baro_rate: int | None = Field(None, description="Rate of change of barometric altitude in feet/minute")
    geom_rate: int | None = Field(None, description="Rate of change of geometric altitude in feet/minute")

    # Speed
    gs: float | None = Field(None, description="Ground speed in knots")
    ias: int | None = Field(None, description="Indicated airspeed in knots")
    tas: int | None = Field(None, description="True airspeed in knots")
    mach: float | None = Field(None, description="Mach number")

    # Heading/Track
    track: float | None = Field(None, description="Track over ground in degrees")
    track_rate: float | None = Field(None, description="Rate of change of track in degrees/second")
    roll: float | None = Field(None, description="Roll angle in degrees")
    mag_heading: float | None = Field(None, description="Magnetic heading in degrees")
    true_heading: float | None = Field(None, description="True heading in degrees")

    # Navigation
    nav_qnh: float | None = Field(None, description="QNH setting in millibars")
    nav_altitude_mcp: int | None = Field(None, description="Selected altitude from MCP/FCU in feet")
    nav_altitude_fms: int | None = Field(None, description="Selected altitude from FMS in feet")
    nav_heading: float | None = Field(None, description="Selected heading in degrees")
    nav_modes: list[str] | None = Field(None, description="Navigation modes")

    # Emergency/Status
    emergency: str | None = Field(None, description="Emergency/priority status")
    flight_status: str | None = Field(None, description="Flight status description")
    alert: int | None = Field(None, description="Alert flag")
    spi: int | None = Field(None, description="Special Position Indicator flag")

    # Accuracy/Quality
    nic: int | None = Field(None, description="Navigation Integrity Category")
    rc: int | None = Field(None, description="Radius of Containment in meters")
    version: int | None = Field(None, description="ADS-B version number")
    nic_baro: int | None = Field(None, description="NIC for barometric altitude")
    nac_p: int | None = Field(None, description="Navigation Accuracy Category - Position")
    nac_v: int | None = Field(None, description="Navigation Accuracy Category - Velocity")
    sil: int | None = Field(None, description="Source Integrity Level")
    sil_type: str | None = Field(None, description="SIL supplement type")
    gva: int | None = Field(None, description="Geometric Vertical Accuracy")
    sda: int | None = Field(None, description="System Design Assurance")

    # Source
    mlat: list[str] | None = Field(None, description="Position from multilateration")
    tisb: list[str] | None = Field(None, description="Position from TIS-B")

    # Reception
    messages: int | None = Field(None, description="Total Mode S messages received")
    seen: float | None = Field(None, description="Seconds since any message last received")
    rssi: float | None = Field(None, description="Signal strength in dBFS")

    # Distance/Direction
    dst: float | None = Field(None, description="Distance from receiver in nautical miles")
    dir: float | None = Field(None, description="Direction from receiver in degrees")

    # Database fields
    dbFlags: int | None = Field(None, description="Database flags")
    year: str | None = Field(None, description="Year of manufacture")

    @property
    def has_position(self) -> bool:
        """Check if aircraft has valid position data.

        Returns:
            True if both latitude and longitude are available, False otherwise.
        """
        return self.lat is not None and self.lon is not None

    @property
    def position_age(self) -> float | None:
        """Get the age of position data in seconds.

        Returns:
            The number of seconds since the position was last updated,
            or None if position age is not available.
        """
        return self.seen_pos

    @property
    def callsign(self) -> str | None:
        """Alias for flight field.

        Returns:
            The aircraft callsign/flight number, or None if not available.
        """
        return self.flight

    def __str__(self) -> str:
        """Return a human-readable string representation.

        Returns:
            A string with hex code, callsign (if available), and position status.
        """
        callsign = f" ({self.flight})" if self.flight else ""
        position = f" at {self.lat:.4f}, {self.lon:.4f}" if self.has_position else " (no position)"
        return f"Aircraft {self.hex}{callsign}{position}"
