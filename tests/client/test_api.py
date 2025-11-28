"""Tests for ReAPIClient class."""

import json
from pathlib import Path

import httpx
import pytest
import respx

from skysnoop.client.api import ReAPIClient
from skysnoop.exceptions import APIError
from skysnoop.models.response import APIResponse
from skysnoop.query.filters import QueryFilters


@pytest.fixture
def api_responses_dir():
    """Get path to API response fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "api_responses"


@pytest.fixture
def circle_response_data(api_responses_dir):
    """Load circle query response fixture."""
    with open(api_responses_dir / "circle_multiple_aircraft.json") as f:
        return json.load(f)


@pytest.fixture
def single_aircraft_response_data(api_responses_dir):
    """Load single aircraft response fixture."""
    with open(api_responses_dir / "circle_single_aircraft.json") as f:
        return json.load(f)


@pytest.fixture
def closest_response_data(api_responses_dir):
    """Load closest response fixture."""
    with open(api_responses_dir / "closest_response.json") as f:
        return json.load(f)


@pytest.fixture
def box_response_data(api_responses_dir):
    """Load box response fixture."""
    with open(api_responses_dir / "box_response.json") as f:
        return json.load(f)


@pytest.fixture
def find_hex_response_data(api_responses_dir):
    """Load find_hex response fixture."""
    with open(api_responses_dir / "find_hex_success.json") as f:
        return json.load(f)


@pytest.fixture
def find_callsign_response_data(api_responses_dir):
    """Load find_callsign response fixture."""
    with open(api_responses_dir / "find_callsign_multiple.json") as f:
        return json.load(f)


@pytest.fixture
def all_with_pos_response_data(api_responses_dir):
    """Load all_with_pos response fixture."""
    with open(api_responses_dir / "all_with_pos_sample.json") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    client = ReAPIClient()

    assert client.base_url == "https://re-api.adsb.lol/"
    assert client.timeout == 30.0
    assert client._http_client is None


@pytest.mark.asyncio
async def test_client_custom_initialization():
    """Test client initialization with custom parameters."""
    client = ReAPIClient(base_url="https://custom.api/", timeout=60.0)

    assert client.base_url == "https://custom.api/"
    assert client.timeout == 60.0


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    async with ReAPIClient() as client:
        assert client._http_client is not None

    # Client should be cleaned up after exit
    assert client._http_client is None


@pytest.mark.asyncio
@respx.mock
async def test_circle_query(circle_response_data):
    """Test circle query method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?circle=37.7749,-122.4194,200").mock(
        return_value=httpx.Response(200, json=circle_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.circle(lat=37.7749, lon=-122.4194, radius=200)

        assert isinstance(response, APIResponse)
        assert response.resultCount > 0
        assert len(response.aircraft) == response.resultCount


@pytest.mark.asyncio
@respx.mock
async def test_circle_query_with_filters(circle_response_data):
    """Test circle query with filters."""
    base_url = "https://re-api.adsb.lol"
    filters = QueryFilters(type_code="A321")

    respx.get(f"{base_url}?circle=37.7749,-122.4194,200&filter_type=A321").mock(
        return_value=httpx.Response(200, json=circle_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
@respx.mock
async def test_closest_query(closest_response_data):
    """Test closest query method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?closest=37.7749,-122.4194,500").mock(
        return_value=httpx.Response(200, json=closest_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.closest(lat=37.7749, lon=-122.4194, radius=500)

        assert isinstance(response, APIResponse)
        assert len(response.aircraft) <= 1


@pytest.mark.asyncio
@respx.mock
async def test_box_query(box_response_data):
    """Test box query method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?box=37.0,38.5,-123.0,-121.0").mock(return_value=httpx.Response(200, json=box_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.box(
            lat_south=37.0,
            lat_north=38.5,
            lon_west=-123.0,
            lon_east=-121.0,
        )

        assert isinstance(response, APIResponse)
        assert response.resultCount >= 0


@pytest.mark.asyncio
@respx.mock
async def test_find_hex(find_hex_response_data):
    """Test find_hex method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?find_hex=a12345").mock(return_value=httpx.Response(200, json=find_hex_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.find_hex("a12345")

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
@respx.mock
async def test_find_callsign(find_callsign_response_data):
    """Test find_callsign method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?find_callsign=UAL123").mock(
        return_value=httpx.Response(200, json=find_callsign_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.find_callsign("UAL123")

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
@respx.mock
async def test_find_reg(find_hex_response_data):
    """Test find_reg method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?find_reg=N12345").mock(return_value=httpx.Response(200, json=find_hex_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.find_reg("N12345")

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
@respx.mock
async def test_find_type(find_callsign_response_data):
    """Test find_type method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?find_type=A321").mock(return_value=httpx.Response(200, json=find_callsign_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.find_type("A321")

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
@respx.mock
async def test_all_with_pos(all_with_pos_response_data):
    """Test all_with_pos method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?all_with_pos").mock(return_value=httpx.Response(200, json=all_with_pos_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.all_with_pos()

        assert isinstance(response, APIResponse)
        assert response.resultCount > 0


@pytest.mark.asyncio
@respx.mock
async def test_all(circle_response_data):
    """Test all method."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?all").mock(return_value=httpx.Response(200, json=circle_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.all()

        assert isinstance(response, APIResponse)


@pytest.mark.asyncio
async def test_method_without_context_manager():
    """Test that methods raise error when called outside context manager."""
    client = ReAPIClient()

    with pytest.raises(RuntimeError, match="not initialized"):
        await client.circle(lat=37.7749, lon=-122.4194, radius=200)


@pytest.mark.asyncio
@respx.mock
async def test_error_handling(circle_response_data):
    """Test error handling for API errors."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?circle=37.7749,-122.4194,200").mock(return_value=httpx.Response(400, text="Bad Request"))

    async with ReAPIClient(base_url=base_url) as client:
        with pytest.raises(APIError, match="400"):
            await client.circle(lat=37.7749, lon=-122.4194, radius=200)


@pytest.mark.asyncio
@respx.mock
async def test_connection_reuse(circle_response_data):
    """Test that HTTP client connection is reused across requests."""
    base_url = "https://re-api.adsb.lol"

    respx.get(f"{base_url}?circle=1,2,100").mock(return_value=httpx.Response(200, json=circle_response_data))
    respx.get(f"{base_url}?circle=3,4,200").mock(return_value=httpx.Response(200, json=circle_response_data))

    async with ReAPIClient(base_url=base_url) as client:
        # Make multiple requests with the same client
        response1 = await client.circle(lat=1, lon=2, radius=100)
        response2 = await client.circle(lat=3, lon=4, radius=200)

        assert isinstance(response1, APIResponse)
        assert isinstance(response2, APIResponse)
        # Same HTTP client should be used
        assert client._http_client is not None


@pytest.mark.asyncio
@respx.mock
async def test_response_iteration(circle_response_data):
    """Test that APIResponse can be iterated."""
    base_url = "https://re-api.adsb.lol"
    respx.get(f"{base_url}?circle=37.7749,-122.4194,200").mock(
        return_value=httpx.Response(200, json=circle_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response = await client.circle(lat=37.7749, lon=-122.4194, radius=200)

        # Test iteration
        aircraft_count = 0
        for aircraft in response:
            aircraft_count += 1
            assert aircraft.hex is not None

        assert aircraft_count == response.resultCount


@pytest.mark.asyncio
@respx.mock
async def test_filters_with_multiple_methods(circle_response_data, box_response_data):
    """Test that filters work with multiple query methods."""
    base_url = "https://re-api.adsb.lol"
    filters = QueryFilters(above_alt_baro=20000)

    respx.get(f"{base_url}?circle=37.7749,-122.4194,200&filter_above_alt_baro=20000").mock(
        return_value=httpx.Response(200, json=circle_response_data)
    )
    respx.get(f"{base_url}?box=37.0,38.5,-123.0,-121.0&filter_above_alt_baro=20000").mock(
        return_value=httpx.Response(200, json=box_response_data)
    )

    async with ReAPIClient(base_url=base_url) as client:
        response1 = await client.circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)
        response2 = await client.box(
            lat_south=37.0,
            lat_north=38.5,
            lon_west=-123.0,
            lon_east=-121.0,
            filters=filters,
        )

        assert isinstance(response1, APIResponse)
        assert isinstance(response2, APIResponse)
