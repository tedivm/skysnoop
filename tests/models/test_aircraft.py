"""Tests for Aircraft model."""

import pytest

from skysnoop.models import Aircraft


def test_aircraft_minimal():
    """Test Aircraft model with minimal required fields."""
    aircraft = Aircraft(hex="a12345")
    assert aircraft.hex == "a12345"
    assert aircraft.flight is None
    assert aircraft.lat is None
    assert aircraft.lon is None
    assert not aircraft.has_position


def test_aircraft_complete(load_api_response):
    """Test Aircraft model with complete data from real API response."""
    data = load_api_response("circle_multiple_aircraft.json")
    aircraft_data = data["aircraft"][0]

    aircraft = Aircraft(**aircraft_data)

    # Verify required field exists
    assert aircraft.hex is not None
    assert len(aircraft.hex) == 6  # ICAO hex is 6 characters

    # Verify identification fields are properly parsed
    if aircraft.flight:
        assert isinstance(aircraft.flight, str)
        assert aircraft.callsign == aircraft.flight  # Test alias works

    if aircraft.type:
        assert isinstance(aircraft.type, str)

    if aircraft.registration:
        assert isinstance(aircraft.registration, str)

    # Verify position if present
    if aircraft.lat is not None and aircraft.lon is not None:
        assert aircraft.has_position
        assert -90 <= aircraft.lat <= 90
        assert -180 <= aircraft.lon <= 180

    # Verify altitude if present
    if aircraft.alt_baro is not None:
        assert isinstance(aircraft.alt_baro, (int, float))

    # Verify speed if present
    if aircraft.gs is not None:
        assert isinstance(aircraft.gs, (int, float))
        assert aircraft.gs >= 0


def test_aircraft_partial(load_api_response):
    """Test Aircraft model with partial data from real API response."""
    data = load_api_response("circle_multiple_aircraft.json")
    # Find an aircraft with fewer fields (iterate to find one)
    aircraft_data = None
    for ac in data["aircraft"]:
        # Find one without type or flight to test partial data
        if not ac.get("t") or not ac.get("flight"):
            aircraft_data = ac
            break

    # If no partial aircraft found, use the last one
    if aircraft_data is None:
        aircraft_data = data["aircraft"][-1]

    aircraft = Aircraft(**aircraft_data)

    # Should have at least hex
    assert aircraft.hex is not None
    # Some fields might be None for partial data
    # Just verify it parses successfully


def test_aircraft_no_position(load_api_response):
    """Test Aircraft without position data."""
    aircraft = Aircraft(hex="test123", alt_baro=30000, gs=400.0)

    assert aircraft.hex == "test123"
    assert not aircraft.has_position
    assert aircraft.position_age is None


def test_aircraft_latitude_validation():
    """Test that latitude validation works correctly."""
    # Valid latitudes
    Aircraft(hex="test", lat=0.0, lon=0.0)
    Aircraft(hex="test", lat=90.0, lon=0.0)
    Aircraft(hex="test", lat=-90.0, lon=0.0)

    # Invalid latitudes should raise validation error
    with pytest.raises(Exception):  # Pydantic ValidationError
        Aircraft(hex="test", lat=91.0, lon=0.0)

    with pytest.raises(Exception):
        Aircraft(hex="test", lat=-91.0, lon=0.0)


def test_aircraft_longitude_validation():
    """Test that longitude validation works correctly."""
    # Valid longitudes
    Aircraft(hex="test", lat=0.0, lon=0.0)
    Aircraft(hex="test", lat=0.0, lon=180.0)
    Aircraft(hex="test", lat=0.0, lon=-180.0)

    # Invalid longitudes should raise validation error
    with pytest.raises(Exception):  # Pydantic ValidationError
        Aircraft(hex="test", lat=0.0, lon=181.0)

    with pytest.raises(Exception):
        Aircraft(hex="test", lat=0.0, lon=-181.0)


def test_aircraft_string_representation():
    """Test Aircraft string representation."""
    # With flight and position
    aircraft = Aircraft(hex="a12345", flight="UAL123", lat=37.5, lon=-122.4)
    str_repr = str(aircraft)
    assert "a12345" in str_repr
    assert "UAL123" in str_repr
    assert "37.5" in str_repr
    assert "-122.4" in str_repr

    # Without flight
    aircraft = Aircraft(hex="a12345", lat=37.5, lon=-122.4)
    str_repr = str(aircraft)
    assert "a12345" in str_repr
    assert "37.5" in str_repr

    # Without position
    aircraft = Aircraft(hex="a12345")
    str_repr = str(aircraft)
    assert "a12345" in str_repr
    assert "no position" in str_repr


def test_aircraft_serialization(load_api_response):
    """Test Aircraft serialization to dict and JSON."""
    data = load_api_response("circle_single_aircraft.json")
    aircraft_data = data["aircraft"][0]

    aircraft = Aircraft(**aircraft_data)

    # Convert to dict
    aircraft_dict = aircraft.model_dump()
    assert "hex" in aircraft_dict
    assert aircraft_dict["hex"] == aircraft.hex
    if aircraft.flight:
        assert aircraft_dict["flight"] == aircraft.flight

    # Convert to JSON
    aircraft_json = aircraft.model_dump_json()
    assert isinstance(aircraft_json, str)
    assert aircraft.hex in aircraft_json


def test_aircraft_forward_compatibility(load_api_response):
    """Test that Aircraft model handles unknown fields gracefully."""
    data = load_api_response("circle_single_aircraft.json")
    aircraft_data = data["aircraft"][0].copy()

    # Add unknown fields
    aircraft_data["unknown_field"] = "test_value"
    aircraft_data["future_feature"] = 12345

    # Should not raise an error due to extra="allow"
    aircraft = Aircraft(**aircraft_data)
    assert aircraft.hex is not None


def test_aircraft_optional_fields():
    """Test that all fields except hex are optional."""
    # Only hex is required
    aircraft = Aircraft(hex="test")
    assert aircraft.hex == "test"

    # All other fields should be None by default
    assert aircraft.flight is None
    assert aircraft.lat is None
    assert aircraft.lon is None
    assert aircraft.alt_baro is None
    assert aircraft.gs is None
    assert aircraft.track is None
