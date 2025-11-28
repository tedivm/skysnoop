"""Tests for OpenAPI client."""

import json
from pathlib import Path

import pytest
import respx
from httpx import Response

from skysnoop.client.openapi import OpenAPIClient
from skysnoop.exceptions import APIError, AuthenticationError, OpenAPIValidationError, RateLimitError
from skysnoop.exceptions import TimeoutError as ADSBTimeoutError
from skysnoop.models.openapi import V2ResponseModel


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
async def test_client_initialization():
    """Test OpenAPIClient can be initialized."""
    client = OpenAPIClient()
    assert client.base_url == "https://api.adsb.lol"
    assert client.timeout == 30.0
    assert client.api_key is None
    assert client.v2 is not None
    assert client.v0 is not None


@pytest.mark.asyncio
async def test_client_initialization_with_api_key():
    """Test OpenAPIClient initialization with API key."""
    client = OpenAPIClient(api_key="test-key-123")
    assert client.api_key == "test-key-123"


@pytest.mark.asyncio
async def test_client_initialization_custom_url():
    """Test OpenAPIClient with custom base URL."""
    client = OpenAPIClient(base_url="https://custom.api.example.com/")
    assert client.base_url == "https://custom.api.example.com"  # Trailing slash stripped


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test OpenAPIClient async context manager."""
    async with OpenAPIClient() as client:
        assert client._client is not None

    # After exiting context, client should be closed
    assert client._client is None


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_mil(load_openapi_response):
    """Test v2.get_mil() method."""
    data = load_openapi_response("v2_mil_response.json")

    route = respx.get("https://api.adsb.lol/v2/mil").mock(return_value=Response(200, json=data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_mil()

    assert route.called
    assert isinstance(response, V2ResponseModel)
    assert response.total > 0


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_pia(load_openapi_response):
    """Test v2.get_pia() method."""
    data = load_openapi_response("v2_pia_response.json")

    route = respx.get("https://api.adsb.lol/v2/pia").mock(return_value=Response(200, json=data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_pia()

    assert route.called
    assert isinstance(response, V2ResponseModel)


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_by_hex(load_openapi_response):
    """Test v2.get_by_hex() method."""
    data = load_openapi_response("v2_hex_single.json")

    route = respx.get("https://api.adsb.lol/v2/hex/ae5a06").mock(return_value=Response(200, json=data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_by_hex(icao_hex="ae5a06")

    assert route.called
    assert isinstance(response, V2ResponseModel)
    assert response.total == 1
    assert response.ac[0].hex == "ae5a06"


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_by_hex_zero_results(load_openapi_response):
    """Test v2.get_by_hex() with zero results."""
    data = load_openapi_response("v2_hex_zero_results.json")

    route = respx.get("https://api.adsb.lol/v2/hex/000000").mock(return_value=Response(200, json=data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_by_hex(icao_hex="000000")

    assert route.called
    assert response.total == 0
    assert len(response.ac) == 0


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_by_point(load_openapi_response):
    """Test v2.get_by_point() method."""
    data = load_openapi_response("v2_point_response.json")

    route = respx.get("https://api.adsb.lol/v2/point/37.7749/-122.4194/50").mock(return_value=Response(200, json=data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_by_point(lat=37.7749, lon=-122.4194, radius=50)

    assert route.called
    assert isinstance(response, V2ResponseModel)


@pytest.mark.asyncio
@respx.mock
async def test_v2_get_by_callsign():
    """Test v2.get_by_callsign() method."""
    mock_data = {
        "ac": [],
        "ctime": 1234567890,
        "msg": "No error",
        "now": 1234567890,
        "ptime": 0,
        "total": 0,
    }

    route = respx.get("https://api.adsb.lol/v2/callsign/UAL123").mock(return_value=Response(200, json=mock_data))

    async with OpenAPIClient() as client:
        response = await client.v2.get_by_callsign(callsign="UAL123")

    assert route.called
    assert isinstance(response, V2ResponseModel)


@pytest.mark.asyncio
@respx.mock
async def test_validation_error_422():
    """Test handling of 422 validation errors."""
    error_data = {
        "detail": [
            {
                "loc": ["path", "lat"],
                "msg": "ensure this value is greater than or equal to -90",
                "type": "value_error.number.not_ge",
            }
        ]
    }

    route = respx.get("https://api.adsb.lol/v2/point/999/0/50").mock(return_value=Response(422, json=error_data))

    with pytest.raises(OpenAPIValidationError) as exc_info:
        async with OpenAPIClient() as client:
            await client.v2.get_by_point(lat=999, lon=0, radius=50)

    assert route.called
    assert exc_info.value.status_code == 422
    assert len(exc_info.value.details) > 0


@pytest.mark.asyncio
@respx.mock
async def test_authentication_error_401():
    """Test handling of 401 authentication errors."""
    route = respx.get("https://api.adsb.lol/v0/me").mock(return_value=Response(401, text="Unauthorized"))

    with pytest.raises(AuthenticationError):
        async with OpenAPIClient() as client:
            await client.v0.get_me()

    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_error_429():
    """Test handling of 429 rate limit errors."""
    route = respx.get("https://api.adsb.lol/v2/mil").mock(
        return_value=Response(
            429,
            headers={"Retry-After": "60"},
            text="Too many requests",
        )
    )

    with pytest.raises(RateLimitError) as exc_info:
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called
    assert exc_info.value.retry_after == 60


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_error_429_no_retry_after():
    """Test 429 error without Retry-After header."""
    route = respx.get("https://api.adsb.lol/v2/mil").mock(return_value=Response(429, text="Too many requests"))

    with pytest.raises(RateLimitError) as exc_info:
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called
    assert exc_info.value.retry_after is None


@pytest.mark.asyncio
@respx.mock
async def test_http_error_500():
    """Test handling of 500 server errors."""
    route = respx.get("https://api.adsb.lol/v2/mil").mock(return_value=Response(500, text="Internal Server Error"))

    with pytest.raises(APIError):
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_network_error():
    """Test handling of network errors."""
    import httpx

    route = respx.get("https://api.adsb.lol/v2/mil").mock(side_effect=httpx.ConnectError("Connection failed"))

    with pytest.raises(APIError):
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_timeout_error():
    """Test handling of timeout errors."""
    import httpx

    route = respx.get("https://api.adsb.lol/v2/mil").mock(side_effect=httpx.TimeoutException("Request timed out"))

    with pytest.raises(ADSBTimeoutError):
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_invalid_json_response():
    """Test handling of invalid JSON responses."""
    route = respx.get("https://api.adsb.lol/v2/mil").mock(return_value=Response(200, text="Not valid JSON"))

    with pytest.raises(APIError):
        async with OpenAPIClient() as client:
            await client.v2.get_mil()

    assert route.called


@pytest.mark.asyncio
async def test_client_without_context_manager():
    """Test that using client without context manager raises error."""
    client = OpenAPIClient()

    with pytest.raises(RuntimeError, match="not initialized"):
        await client.v2.get_mil()


@pytest.mark.asyncio
@respx.mock
async def test_api_key_in_headers():
    """Test that API key is included in request headers."""
    mock_data = {
        "ac": [],
        "ctime": 1234567890,
        "msg": "No error",
        "now": 1234567890,
        "ptime": 0,
        "total": 0,
    }

    route = respx.get("https://api.adsb.lol/v2/mil").mock(return_value=Response(200, json=mock_data))

    async with OpenAPIClient(api_key="test-key-123") as client:
        await client.v2.get_mil()

    assert route.called
    # Check that Authorization header was sent
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-key-123"


@pytest.mark.asyncio
@respx.mock
async def test_all_v2_methods():
    """Test that all v2 methods can be called."""
    mock_data = {
        "ac": [],
        "ctime": 1234567890,
        "msg": "No error",
        "now": 1234567890,
        "ptime": 0,
        "total": 0,
    }

    respx.route().mock(return_value=Response(200, json=mock_data))

    async with OpenAPIClient() as client:
        # Test all v2 methods exist and are callable
        await client.v2.get_ladd()
        await client.v2.get_by_squawk("7700")
        await client.v2.get_by_type("B738")
        await client.v2.get_by_registration("N12345")
        await client.v2.get_closest(37.7749, -122.4194, 50)


@pytest.mark.asyncio
@respx.mock
async def test_v0_get_airport():
    """Test v0.get_airport() method."""
    mock_data = {"icao": "KSFO", "name": "San Francisco International Airport"}

    route = respx.get("https://api.adsb.lol/v0/airport/KSFO").mock(return_value=Response(200, json=mock_data))

    async with OpenAPIClient() as client:
        response = await client.v0.get_airport(icao="KSFO")

    assert route.called
    assert isinstance(response, dict)
    assert response["icao"] == "KSFO"
