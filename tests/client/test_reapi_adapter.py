"""Tests for ReAPIAdapter backend adapter."""

import json
from pathlib import Path

import pytest
import pytest_asyncio
import respx
from httpx import Response

from skysnoop.client.adapters.reapi_adapter import ReAPIAdapter
from skysnoop.models import Aircraft, SkyData
from skysnoop.query.filters import QueryFilters
from tests.client.test_protocol_compliance import BaseProtocolTestSuite


@pytest.fixture
def api_responses_dir() -> Path:
    """Return the path to the API responses fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "api_responses"


@pytest.fixture
def load_api_response(api_responses_dir: Path):
    """Load an API response fixture from a JSON file."""

    def _load(filename: str) -> dict:
        filepath = api_responses_dir / filename
        with open(filepath) as f:
            return json.load(f)

    return _load


@pytest.mark.usefixtures("respx_mock")
class TestReAPIAdapterProtocolCompliance(BaseProtocolTestSuite):
    """Test ReAPIAdapter compliance with BackendProtocol.

    Inherits shared protocol tests from BaseProtocolTestSuite. This ensures
    the adapter implements all required methods and returns SkyData instances.
    """

    @pytest_asyncio.fixture
    async def adapter(self, load_api_response, respx_mock):
        """Provide ReAPIAdapter instance for protocol tests."""
        # Mock all endpoints with sample responses
        # QueryBuilder uses underscore format: find_hex, find_callsign, find_reg, find_type
        hex_data = load_api_response("find_hex_success.json")
        respx_mock.get(url__regex=r".*\?find_hex=abc123").mock(return_value=Response(200, json=hex_data))

        callsign_data = load_api_response("find_callsign_multiple.json")
        respx_mock.get(url__regex=r".*\?find_callsign=TEST123").mock(return_value=Response(200, json=callsign_data))

        reg_data = load_api_response("find_reg_response.json")
        respx_mock.get(url__regex=r".*\?find_reg=N12345").mock(return_value=Response(200, json=reg_data))

        type_data = load_api_response("find_type_response.json")
        respx_mock.get(url__regex=r".*\?find_type=B738").mock(return_value=Response(200, json=type_data))

        circle_data = load_api_response("circle_single_aircraft.json")
        respx_mock.get(url__regex=r".*\?circle=.*").mock(return_value=Response(200, json=circle_data))

        closest_data = load_api_response("closest_response.json")
        respx_mock.get(url__regex=r".*\?closest=.*").mock(return_value=Response(200, json=closest_data))

        box_data = load_api_response("box_response.json")
        respx_mock.get(url__regex=r".*\?box=.*").mock(return_value=Response(200, json=box_data))

        all_with_pos_data = load_api_response("all_with_pos_sample.json")
        respx_mock.get(url__regex=r".*\?all_with_pos.*").mock(return_value=Response(200, json=all_with_pos_data))

        async with ReAPIAdapter() as adapter:
            yield adapter


@pytest.mark.asyncio
@respx.mock
async def test_reapi_adapter_initialization():
    """Test ReAPIAdapter initialization."""
    adapter = ReAPIAdapter()
    assert adapter._client is not None


@pytest.mark.asyncio
@respx.mock
async def test_reapi_adapter_context_manager():
    """Test ReAPIAdapter async context manager."""
    async with ReAPIAdapter() as adapter:
        assert adapter._client._http_client is not None

    assert adapter._client._http_client is None


@pytest.mark.asyncio
@respx.mock
async def test_api_response_to_skydata_conversion(load_api_response):
    """Test conversion from APIResponse to SkyData."""
    data = load_api_response("find_hex_success.json")
    route = respx.get(url__regex=r".*\?find_hex=abc123").mock(return_value=Response(200, json=data))

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_by_hex("abc123")

    assert route.called
    assert isinstance(result, SkyData)
    assert result.backend == "reapi"
    assert result.simulated is False
    assert isinstance(result.processing_time, float)  # RE-API provides processing time
    assert result.processing_time is not None
    assert isinstance(result.timestamp, float)
    assert result.timestamp > 0
    assert result.result_count >= 0
    assert isinstance(result.aircraft, list)


@pytest.mark.asyncio
@respx.mock
async def test_aircraft_list_preserved(load_api_response):
    """Test that Aircraft instances are preserved from APIResponse."""
    data = load_api_response("find_hex_success.json")
    respx.get(url__regex=r".*\?find_hex=test123").mock(return_value=Response(200, json=data))

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_by_hex("test123")

    assert len(result.aircraft) > 0
    aircraft = result.aircraft[0]
    assert isinstance(aircraft, Aircraft)
    assert aircraft.hex is not None


@pytest.mark.asyncio
@respx.mock
async def test_filters_passed_through(load_api_response):
    """Test that QueryFilters are passed through to RE-API."""
    data = load_api_response("circle_single_aircraft.json")
    route = respx.get(url__regex=r".*\?circle=.*").mock(return_value=Response(200, json=data))

    filters = QueryFilters(military=True)

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_in_circle(lat=37.0, lon=-122.0, radius=50.0, filters=filters)

    assert route.called
    assert isinstance(result, SkyData)


@pytest.mark.asyncio
@respx.mock
async def test_box_query_native_support(load_api_response):
    """Test that box queries use native RE-API support (not simulated)."""
    data = load_api_response("box_response.json")
    route = respx.get(url__regex=r".*/\?box=.*").mock(return_value=Response(200, json=data))

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )

    assert route.called
    assert isinstance(result, SkyData)
    assert result.simulated is False  # RE-API has native box support


@pytest.mark.asyncio
@respx.mock
async def test_all_with_pos_native_support(load_api_response):
    """Test that all_with_pos uses native RE-API support."""
    data = load_api_response("all_with_pos_sample.json")
    route = respx.get(url__regex=r".*\?all_with_pos.*").mock(return_value=Response(200, json=data))

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_all_with_pos()

    assert route.called
    assert isinstance(result, SkyData)
    assert result.simulated is False  # RE-API has native support


@pytest.mark.asyncio
@respx.mock
async def test_all_with_pos_with_filters(load_api_response):
    """Test all_with_pos with filters."""
    data = load_api_response("all_with_pos_sample.json")
    route = respx.get(url__regex=r".*\?all_with_pos.*").mock(return_value=Response(200, json=data))

    filters = QueryFilters(military=True)

    async with ReAPIAdapter() as adapter:
        result = await adapter.get_all_with_pos(filters=filters)

    assert route.called
    assert isinstance(result, SkyData)


@pytest.mark.asyncio
@respx.mock
async def test_custom_base_url():
    """Test ReAPIAdapter with custom base URL."""
    data = {"now": 1234567890.5, "resultCount": 0, "ptime": 5.5, "aircraft": []}
    respx.get(url__regex=r"https://custom.example.com/.*").mock(return_value=Response(200, json=data))

    async with ReAPIAdapter(base_url="https://custom.example.com/") as adapter:
        result = await adapter.get_by_hex("abc123")

    assert isinstance(result, SkyData)
    assert result.backend == "reapi"
