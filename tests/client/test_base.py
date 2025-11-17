"""Tests for BaseHTTPClient class."""

import json
from pathlib import Path

import httpx
import pytest
import respx

from adsblol.client.base import BaseHTTPClient
from adsblol.exceptions import APIError
from adsblol.exceptions import TimeoutError as ADSBTimeoutError


@pytest.fixture
def api_responses_dir():
    """Get path to API response fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "api_responses"


@pytest.fixture
def circle_response_data(api_responses_dir):
    """Load circle query response fixture."""
    with open(api_responses_dir / "circle_multiple_aircraft.json") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization with default settings."""
    client = BaseHTTPClient(base_url="https://re-api.adsb.lol/", timeout=30.0)

    assert client.base_url == "https://re-api.adsb.lol"
    assert client.timeout == 30.0
    assert client._client is None


@pytest.mark.asyncio
async def test_client_initialization_strips_trailing_slash():
    """Test that trailing slash is removed from base URL."""
    client = BaseHTTPClient(base_url="https://re-api.adsb.lol/")

    assert client.base_url == "https://re-api.adsb.lol"


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        assert client._client is not None
        assert isinstance(client._client, httpx.AsyncClient)

    # Client should be closed after context exit
    assert client._client is None


@pytest.mark.asyncio
async def test_client_user_agent_header():
    """Test that client sets proper User-Agent header."""
    from adsblol import __version__

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        assert client._client is not None
        # Check that User-Agent header is set
        assert "User-Agent" in client._client.headers
        assert client._client.headers["User-Agent"] == f"adsblol/{__version__}"


@pytest.mark.asyncio
async def test_client_follow_redirects():
    """Test that client follows redirects automatically."""
    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        assert client._client is not None
        assert client._client.follow_redirects is True


@pytest.mark.asyncio
@respx.mock
async def test_client_get_success(circle_response_data):
    """Test successful GET request."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200"

    # Mock the API response
    respx.get(f"{base_url}?{query_string}").mock(return_value=httpx.Response(200, json=circle_response_data))

    async with BaseHTTPClient(base_url=base_url) as client:
        response = await client.get(query_string)

        assert "aircraft" in response
        assert "now" in response
        assert "resultCount" in response
        assert isinstance(response["aircraft"], list)


@pytest.mark.asyncio
@respx.mock
async def test_client_get_preserves_commas():
    """Test that commas in query string are preserved."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200"

    # Mock to capture the actual URL called
    route = respx.get(f"{base_url}?{query_string}").mock(
        return_value=httpx.Response(200, json={"aircraft": [], "now": 0, "resultCount": 0})
    )

    async with BaseHTTPClient(base_url=base_url) as client:
        await client.get(query_string)

    # Verify the URL contains unencoded commas
    called_url = str(route.calls[0].request.url)
    assert "circle=37.7749,-122.4194,200" in called_url
    assert "%2C" not in called_url


@pytest.mark.asyncio
@respx.mock
async def test_client_get_with_filters():
    """Test GET request with filters appended."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200&filter_type=A321"

    respx.get(f"{base_url}?{query_string}").mock(
        return_value=httpx.Response(200, json={"aircraft": [], "now": 0, "resultCount": 0})
    )

    async with BaseHTTPClient(base_url=base_url) as client:
        response = await client.get(query_string)

        assert response["aircraft"] == []


@pytest.mark.asyncio
@respx.mock
async def test_client_get_http_error():
    """Test GET request with HTTP error status."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=invalid"

    respx.get(f"{base_url}?{query_string}").mock(return_value=httpx.Response(400, text="Bad Request"))

    async with BaseHTTPClient(base_url=base_url) as client:
        with pytest.raises(APIError, match="400"):
            await client.get(query_string)


@pytest.mark.asyncio
@respx.mock
async def test_client_get_timeout():
    """Test GET request timeout."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200"

    respx.get(f"{base_url}?{query_string}").mock(side_effect=httpx.TimeoutException("Timeout"))

    async with BaseHTTPClient(base_url=base_url, timeout=1.0) as client:
        with pytest.raises(ADSBTimeoutError, match="timed out"):
            await client.get(query_string)


@pytest.mark.asyncio
@respx.mock
async def test_client_get_network_error():
    """Test GET request with network error."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200"

    respx.get(f"{base_url}?{query_string}").mock(side_effect=httpx.ConnectError("Connection failed"))

    async with BaseHTTPClient(base_url=base_url) as client:
        with pytest.raises(APIError, match="Connection failed"):
            await client.get(query_string)


@pytest.mark.asyncio
@respx.mock
async def test_client_get_invalid_json():
    """Test GET request with invalid JSON response."""
    base_url = "https://re-api.adsb.lol"
    query_string = "circle=37.7749,-122.4194,200"

    respx.get(f"{base_url}?{query_string}").mock(return_value=httpx.Response(200, text="Not JSON"))

    async with BaseHTTPClient(base_url=base_url) as client:
        with pytest.raises(APIError, match="Invalid JSON"):
            await client.get(query_string)


@pytest.mark.asyncio
async def test_client_get_without_context_manager():
    """Test that GET raises error when called outside context manager."""
    client = BaseHTTPClient(base_url="https://re-api.adsb.lol/")

    with pytest.raises(RuntimeError, match="not initialized"):
        await client.get("circle=37.7749,-122.4194,200")


@pytest.mark.asyncio
@respx.mock
async def test_client_multiple_requests():
    """Test making multiple requests with same client."""
    base_url = "https://re-api.adsb.lol"

    respx.get(f"{base_url}?circle=1,2,100").mock(
        return_value=httpx.Response(200, json={"aircraft": [], "now": 0, "resultCount": 0})
    )
    respx.get(f"{base_url}?circle=3,4,200").mock(
        return_value=httpx.Response(200, json={"aircraft": [], "now": 1, "resultCount": 0})
    )

    async with BaseHTTPClient(base_url=base_url) as client:
        response1 = await client.get("circle=1,2,100")
        response2 = await client.get("circle=3,4,200")

        assert response1["now"] == 0
        assert response2["now"] == 1
        assert response2["now"] == 1
