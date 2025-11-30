"""Tests for OpenAPIAdapter box query simulation and limitations."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from skysnoop.client.adapters.openapi_adapter import OpenAPIAdapter
from skysnoop.models import SkyData


@pytest.fixture
def openapi_responses_dir() -> Path:
    """Return the path to the OpenAPI responses fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "openapi_responses"


@pytest.fixture
def load_openapi_response(openapi_responses_dir: Path):
    """Load an OpenAPI response fixture from a JSON file."""

    def _load(filename: str) -> dict:
        filepath = openapi_responses_dir / filename
        with open(filepath) as f:
            return json.load(f)

    return _load


@pytest.mark.asyncio
@respx.mock
async def test_box_query_simulation(load_openapi_response):
    """Test that box queries are simulated via circle + filtering."""
    data = load_openapi_response("v2_point_response.json")

    # Mock the bounding circle query (adapter calculates center and radius)
    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )

    assert isinstance(result, SkyData)
    assert result.backend == "openapi"
    assert result.simulated is True  # Box query is simulated


@pytest.mark.asyncio
@respx.mock
async def test_box_simulation_filters_correctly(load_openapi_response):
    """Test that box simulation filters aircraft to box bounds."""
    # Create a response with aircraft both inside and outside the box
    data = {
        "ac": [
            # Inside box
            {
                "hex": "inside1",
                "lat": 37.5,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Outside box (south of boundary)
            {
                "hex": "outside1",
                "lat": 36.5,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Outside box (north of boundary)
            {
                "hex": "outside2",
                "lat": 38.5,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Outside box (west of boundary)
            {
                "hex": "outside3",
                "lat": 37.5,
                "lon": -123.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Outside box (east of boundary)
            {
                "hex": "outside4",
                "lat": 37.5,
                "lon": -121.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Inside box (another one)
            {
                "hex": "inside2",
                "lat": 37.8,
                "lon": -122.2,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
        ],
        "ctime": 1234567890,
        "msg": "OK",
        "now": 1234567890,
        "ptime": 10,
        "total": 6,
    }

    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )

    # Should only have the 2 aircraft inside the box
    assert result.result_count == 2
    assert len(result.aircraft) == 2
    hex_codes = {ac.hex for ac in result.aircraft}
    assert hex_codes == {"inside1", "inside2"}


@pytest.mark.asyncio
@respx.mock
async def test_box_longitude_wraparound_handling(load_openapi_response):
    """Test that box simulation handles longitude wraparound correctly."""
    # Box crossing 180° meridian (e.g., in Pacific)
    data = {
        "ac": [
            # Inside box (west side of 180°)
            {
                "hex": "inside1",
                "lat": 30.0,
                "lon": 175.0,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Inside box (east side of 180°)
            {
                "hex": "inside2",
                "lat": 30.0,
                "lon": -175.0,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # Outside box
            {
                "hex": "outside1",
                "lat": 30.0,
                "lon": 0.0,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
        ],
        "ctime": 1234567890,
        "msg": "OK",
        "now": 1234567890,
        "ptime": 10,
        "total": 3,
    }

    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=25.0,
            lat_north=35.0,
            lon_west=170.0,  # West of 180°
            lon_east=-170.0,  # East of 180° (wraparound case)
        )

    # Should have the 2 aircraft inside wraparound box
    assert result.result_count == 2
    hex_codes = {ac.hex for ac in result.aircraft}
    assert hex_codes == {"inside1", "inside2"}


@pytest.mark.asyncio
@respx.mock
async def test_box_empty_results(load_openapi_response):
    """Test box simulation with no aircraft in bounds."""
    data = {
        "ac": [
            # All outside the box
            {
                "hex": "outside1",
                "lat": 10.0,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            {
                "hex": "outside2",
                "lat": 50.0,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
        ],
        "ctime": 1234567890,
        "msg": "OK",
        "now": 1234567890,
        "ptime": 10,
        "total": 2,
    }

    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )

    assert result.result_count == 0
    assert len(result.aircraft) == 0
    assert result.simulated is True


@pytest.mark.asyncio
@respx.mock
async def test_box_filters_aircraft_without_position(load_openapi_response):
    """Test that aircraft without position data are filtered out."""
    data = {
        "ac": [
            # Has position
            {
                "hex": "with_pos",
                "lat": 37.5,
                "lon": -122.5,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
            # No position data
            {
                "hex": "no_pos",
                "lat": None,
                "lon": None,
                "messages": 100,
                "seen": 0.1,
                "rssi": -20,
                "mlat": [],
                "tisb": [],
                "type": "adsb_icao",
            },
        ],
        "ctime": 1234567890,
        "msg": "OK",
        "now": 1234567890,
        "ptime": 10,
        "total": 2,
    }

    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )

    # Should only include the aircraft with position data
    assert result.result_count == 1
    assert result.aircraft[0].hex == "with_pos"


@pytest.mark.asyncio
@respx.mock
async def test_haversine_distance_calculation():
    """Test haversine distance calculation helper."""
    adapter = OpenAPIAdapter()

    # Distance from San Francisco to Los Angeles (approx 302 NM)
    distance = adapter._calculate_haversine_distance(
        lat1=37.7749,
        lon1=-122.4194,
        lat2=34.0522,
        lon2=-118.2437,
    )

    # Should be approximately 302 nautical miles
    assert 300 < distance < 305


@pytest.mark.asyncio
@respx.mock
async def test_is_in_box_helper():
    """Test _is_in_box helper method."""
    from skysnoop.models.openapi.generated import V2ResponseAcItem

    adapter = OpenAPIAdapter()

    # Create test aircraft
    inside = V2ResponseAcItem(
        hex="inside",
        lat=37.5,
        lon=-122.5,
        messages=100,
        seen=0.1,
        rssi=-20,
        mlat=[],
        tisb=[],
        type="adsb_icao",
    )

    outside = V2ResponseAcItem(
        hex="outside",
        lat=36.0,
        lon=-122.5,
        messages=100,
        seen=0.1,
        rssi=-20,
        mlat=[],
        tisb=[],
        type="adsb_icao",
    )

    no_position = V2ResponseAcItem(
        hex="no_pos",
        lat=None,
        lon=None,
        messages=100,
        seen=0.1,
        rssi=-20,
        mlat=[],
        tisb=[],
        type="adsb_icao",
    )

    # Test normal box
    assert adapter._is_in_box(inside, lat_south=37.0, lat_north=38.0, lon_west=-123.0, lon_east=-122.0) is True
    assert adapter._is_in_box(outside, lat_south=37.0, lat_north=38.0, lon_west=-123.0, lon_east=-122.0) is False
    assert adapter._is_in_box(no_position, lat_south=37.0, lat_north=38.0, lon_west=-123.0, lon_east=-122.0) is False
