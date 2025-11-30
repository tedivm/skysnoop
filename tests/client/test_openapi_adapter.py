"""Tests for OpenAPIAdapter backend adapter."""

import json
from pathlib import Path

import pytest
import pytest_asyncio
import respx
from httpx import Response

from skysnoop.client.adapters.openapi_adapter import OpenAPIAdapter
from skysnoop.exceptions import UnsupportedOperationError
from skysnoop.models import Aircraft, SkyData
from tests.client.test_protocol_compliance import BaseProtocolTestSuite


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


@pytest.mark.usefixtures("respx_mock")
class TestOpenAPIAdapterProtocolCompliance(BaseProtocolTestSuite):
    """Test OpenAPIAdapter compliance with BackendProtocol.

    Inherits shared protocol tests from BaseProtocolTestSuite. This ensures
    the adapter implements all required methods and returns SkyData instances.
    """

    @pytest_asyncio.fixture
    async def adapter(self, load_openapi_response, respx_mock):
        """Provide OpenAPIAdapter instance for protocol tests."""
        # Mock all endpoints with sample responses (reusing available fixtures)
        hex_data = load_openapi_response("v2_hex_single.json")
        point_data = load_openapi_response("v2_point_response.json")

        # Use hex_data for all single-aircraft lookups
        respx_mock.get("https://api.adsb.lol/v2/hex/abc123").mock(return_value=Response(200, json=hex_data))
        respx_mock.get("https://api.adsb.lol/v2/callsign/TEST123").mock(return_value=Response(200, json=hex_data))
        respx_mock.get("https://api.adsb.lol/v2/reg/N12345").mock(return_value=Response(200, json=hex_data))
        respx_mock.get("https://api.adsb.lol/v2/type/B738").mock(return_value=Response(200, json=hex_data))

        # Use point_data for spatial queries
        respx_mock.get("https://api.adsb.lol/v2/point/37.7749/-122.4194/50").mock(
            return_value=Response(200, json=point_data)
        )
        respx_mock.get("https://api.adsb.lol/v2/closest/37.7749/-122.4194/50").mock(
            return_value=Response(200, json=point_data)
        )

        # Mock for box simulation (needs a larger radius for bounding circle)
        respx_mock.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=point_data))

        async with OpenAPIAdapter() as adapter:
            yield adapter


@pytest.mark.asyncio
@respx.mock
async def test_openapi_adapter_initialization():
    """Test OpenAPIAdapter initialization."""
    adapter = OpenAPIAdapter()
    assert adapter._client is not None


@pytest.mark.asyncio
@respx.mock
async def test_openapi_adapter_context_manager():
    """Test OpenAPIAdapter async context manager."""
    async with OpenAPIAdapter() as adapter:
        assert adapter._client._client is not None

    assert adapter._client._client is None


@pytest.mark.asyncio
@respx.mock
async def test_v2_response_to_skydata_conversion(load_openapi_response):
    """Test conversion from V2ResponseModel to SkyData."""
    data = load_openapi_response("v2_hex_single.json")
    route = respx.get("https://api.adsb.lol/v2/hex/abc123").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_by_hex("abc123")

    assert route.called
    assert isinstance(result, SkyData)
    assert result.backend == "openapi"
    assert result.simulated is False
    assert result.processing_time is None  # OpenAPI doesn't provide processing time
    assert isinstance(result.timestamp, float)
    assert result.timestamp > 0
    assert result.result_count >= 0
    assert isinstance(result.aircraft, list)


@pytest.mark.asyncio
@respx.mock
async def test_v2_aircraft_to_aircraft_conversion(load_openapi_response):
    """Test conversion from V2ResponseAcItem to Aircraft."""
    data = load_openapi_response("v2_hex_single.json")
    respx.get("https://api.adsb.lol/v2/hex/abc123").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter() as adapter:
        result = await adapter.get_by_hex("abc123")

    assert len(result.aircraft) > 0
    aircraft = result.aircraft[0]
    assert isinstance(aircraft, Aircraft)
    assert aircraft.hex is not None
    # OpenAPI uses 'r' for registration and 't' for type
    # Check that conversion handles these correctly


@pytest.mark.asyncio
@respx.mock
async def test_get_by_hex_with_api_key(load_openapi_response):
    """Test adapter with API key (future compatibility)."""
    data = load_openapi_response("v2_hex_single.json")
    route = respx.get("https://api.adsb.lol/v2/hex/test123").mock(return_value=Response(200, json=data))

    async with OpenAPIAdapter(api_key="test-key") as adapter:
        result = await adapter.get_by_hex("test123")

    assert route.called
    assert isinstance(result, SkyData)
    # Note: API key handling is in OpenAPIClient, not adapter


@pytest.mark.asyncio
@respx.mock
async def test_filters_warning_logged(load_openapi_response, caplog):
    """Test that warning is logged when filters are provided."""
    from skysnoop.query.filters import QueryFilters

    data = load_openapi_response("v2_point_response.json")
    respx.get("https://api.adsb.lol/v2/point/37.0/-122.0/50").mock(return_value=Response(200, json=data))

    filters = QueryFilters(military=True)

    async with OpenAPIAdapter() as adapter:
        await adapter.get_in_circle(lat=37.0, lon=-122.0, radius=50.0, filters=filters)

    # Check that warning was logged
    assert any("OpenAPI does not support QueryFilters" in record.message for record in caplog.records)


@pytest.mark.asyncio
@respx.mock
async def test_filters_warning_logged_in_box(load_openapi_response, caplog):
    """Test that warning is logged when filters are provided to get_in_box."""
    from skysnoop.query.filters import QueryFilters

    data = load_openapi_response("v2_point_response.json")
    respx.get(url__regex=r".*/v2/point/.*").mock(return_value=Response(200, json=data))

    filters = QueryFilters(military=True)

    async with OpenAPIAdapter() as adapter:
        await adapter.get_in_box(lat_south=37.0, lat_north=38.0, lon_west=-123.0, lon_east=-122.0, filters=filters)

    # Check that warning was logged
    assert any("OpenAPI does not support QueryFilters" in record.message for record in caplog.records)


@pytest.mark.asyncio
@respx.mock
async def test_filters_warning_logged_in_closest(load_openapi_response, caplog):
    """Test that warning is logged when filters are provided to get_closest."""
    from skysnoop.query.filters import QueryFilters

    data = load_openapi_response("v2_point_response.json")
    respx.get("https://api.adsb.lol/v2/closest/37.0/-122.0/50").mock(return_value=Response(200, json=data))

    filters = QueryFilters(military=True)

    async with OpenAPIAdapter() as adapter:
        await adapter.get_closest(lat=37.0, lon=-122.0, radius=50.0, filters=filters)

    # Check that warning was logged
    assert any("OpenAPI does not support QueryFilters" in record.message for record in caplog.records)


@pytest.mark.asyncio
@respx.mock
async def test_get_all_with_pos_raises_unsupported():
    """Test that get_all_with_pos raises UnsupportedOperationError."""
    async with OpenAPIAdapter() as adapter:
        with pytest.raises(UnsupportedOperationError) as exc_info:
            await adapter.get_all_with_pos()

    assert "get_all_with_pos() is not supported" in str(exc_info.value)
    assert "250 NM radius limitation" in str(exc_info.value)
    assert "backend='reapi'" in str(exc_info.value)
