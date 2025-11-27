"""Live integration tests for OpenAPI client.

These tests run against the real adsb.lol OpenAPI endpoints.
Run with: pytest --run-live-openapi tests/integration/test_live_openapi.py

Note: Unlike re-api tests, these CAN run in CI as the OpenAPI is globally accessible.
"""

import pytest

from adsblol.client.openapi import OpenAPIClient
from adsblol.models.openapi import V2ResponseModel

# Mark all tests in this module as live_openapi tests
pytestmark = pytest.mark.live_openapi


@pytest.mark.asyncio
async def test_live_v2_mil():
    """Test v2.get_mil() against live API.

    Run with: pytest --run-live-openapi
    """
    async with OpenAPIClient() as client:
        response = await client.v2.get_mil()

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    assert response.now > 0
    # May or may not have results depending on what's flying
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_v2_pia():
    """Test v2.get_pia() against live API."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_pia()

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_v2_ladd():
    """Test v2.get_ladd() against live API."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_ladd()

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_v2_hex_zero_results():
    """Test v2.get_by_hex() with invalid hex returns zero results."""
    async with OpenAPIClient() as client:
        # Use a hex that's extremely unlikely to exist
        response = await client.v2.get_by_hex(icao_hex="zzzzz0")

    assert isinstance(response, V2ResponseModel)
    # Should have zero or very few results for invalid hex
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_v2_point_san_francisco():
    """Test v2.get_by_point() for San Francisco area."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_by_point(
            lat=37.7749,
            lon=-122.4194,
            radius=100,  # 100 nm radius
        )

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    # Should typically have some aircraft in SF area
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_v2_closest():
    """Test v2.get_closest() for closest aircraft."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_closest(
            lat=37.7749,
            lon=-122.4194,
            radius=200,  # 200 nm radius
        )

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    # Should typically return at most 1 aircraft
    assert response.total <= 1


@pytest.mark.asyncio
async def test_live_v2_type_common_aircraft():
    """Test v2.get_by_type() with common aircraft type."""
    async with OpenAPIClient() as client:
        # B738 (Boeing 737-800) is very common
        response = await client.v2.get_by_type(aircraft_type="B738")

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    # Should typically have some B738s flying
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_response_aircraft_has_position():
    """Test that aircraft with positions have valid coordinates."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_mil()

    # Check that aircraft with positions have valid coordinates
    for aircraft in response.ac:
        if aircraft.lat is not None and aircraft.lon is not None:
            assert -90 <= aircraft.lat <= 90
            assert -180 <= aircraft.lon <= 180


@pytest.mark.asyncio
async def test_live_response_timestamps():
    """Test that response timestamps are valid."""
    async with OpenAPIClient() as client:
        response = await client.v2.get_mil()

    # Timestamps should be reasonable (Unix timestamp in milliseconds)
    assert response.now > 1600000000000  # After Sep 2020
    assert response.ctime > 1600000000000
    assert response.ptime >= 0


@pytest.mark.asyncio
async def test_live_v2_squawk_emergency():
    """Test v2.get_by_squawk() for emergency squawk code."""
    async with OpenAPIClient() as client:
        # 7700 is emergency squawk - hopefully nobody is squawking this!
        response = await client.v2.get_by_squawk(squawk="7700")

    assert isinstance(response, V2ResponseModel)
    assert response.msg == "No error"
    assert response.total >= 0


@pytest.mark.asyncio
async def test_live_api_version_logged(caplog):
    """Test that OpenAPI version is logged on client init."""
    import logging

    caplog.set_level(logging.INFO)

    _ = OpenAPIClient()

    assert "OpenAPIClient initialized" in caplog.text
    assert "spec version" in caplog.text
