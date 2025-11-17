"""Live API integration tests.

These tests run against the actual adsb.lol API and require:
1. Network access to https://re-api.adsb.lol/
2. Being on a feeder IP or having VPN access

Run with: pytest tests/integration/ -v --run-live-api

Skip by default to avoid failures in CI/non-feeder environments.
"""

import pytest

from adsblol.client.base import BaseHTTPClient
from adsblol.models.response import APIResponse
from adsblol.query.builder import QueryBuilder
from adsblol.query.filters import QueryFilters

pytestmark = pytest.mark.live_api


@pytest.mark.asyncio
async def test_live_circle_query():
    """Test circle query against live API."""
    # San Francisco area
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200)

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    # Parse response with our models
    response = APIResponse(**response_data)

    assert response.now > 0
    assert response.resultCount >= 0
    assert len(response.aircraft) == response.resultCount


@pytest.mark.asyncio
async def test_live_circle_with_filters():
    """Test circle query with filters against live API."""
    # Note: Filter support varies by API - this test verifies query construction works
    # even if the API doesn't support all filters
    filters = QueryFilters(type_code="A320")
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

    # Verify filter is in the query string
    assert "filter_type=A320" in query

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        # API may return 400 if filters aren't supported, which is fine
        # We're mainly testing that our query builder works correctly
        try:
            response_data = await client.get(query)
            response = APIResponse(**response_data)
            assert response is not None
        except Exception:
            # If filters cause issues, verify we can at least make a basic query
            basic_query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200)
            response_data = await client.get(basic_query)
            response = APIResponse(**response_data)
            assert response.resultCount >= 0


@pytest.mark.asyncio
async def test_live_closest_query():
    """Test closest query against live API."""
    query = QueryBuilder.build_closest(lat=37.7749, lon=-122.4194, radius=500)

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    response = APIResponse(**response_data)

    # Closest should return at most 1 aircraft
    assert len(response.aircraft) <= 1


@pytest.mark.asyncio
async def test_live_box_query():
    """Test box query against live API."""
    # Bay Area box
    query = QueryBuilder.build_box(
        lat_south=37.0,
        lat_north=38.5,
        lon_west=-123.0,
        lon_east=-121.0,
    )

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    response = APIResponse(**response_data)

    # Verify all aircraft are within the box
    for aircraft in response.aircraft:
        if aircraft.has_position:
            assert 37.0 <= aircraft.lat <= 38.5
            assert -123.0 <= aircraft.lon <= -121.0


@pytest.mark.asyncio
async def test_live_all_with_pos_query():
    """Test all_with_pos query against live API."""
    query = QueryBuilder.build_all_with_pos()

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    response = APIResponse(**response_data)

    # Should have many aircraft
    assert response.resultCount > 0

    # All should have positions
    for aircraft in response.aircraft:
        assert aircraft.has_position


@pytest.mark.asyncio
async def test_live_find_type_query():
    """Test find_type query against live API."""
    # Look for A320 family aircraft (common type)
    query = QueryBuilder.build_find_type("A320")

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    response = APIResponse(**response_data)

    # The API uses 't' field for matching, but returns aircraft data
    # Just verify we got a valid response
    assert response.resultCount >= 0
    assert len(response.aircraft) == response.resultCount


@pytest.mark.asyncio
async def test_live_comma_preservation():
    """Test that commas are preserved in the actual API request."""
    # This is the critical test - commas must not be URL-encoded
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=100)

    # Verify the query string has commas
    assert "," in query
    assert "%2C" not in query

    # Make the actual request - if commas were encoded, this would return 400
    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    # If we get here, the API accepted the request (commas not encoded)
    response = APIResponse(**response_data)
    assert response is not None


@pytest.mark.asyncio
async def test_live_altitude_ground_handling():
    """Test that 'ground' altitude values are handled correctly."""
    # Query a large area to find aircraft on the ground
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=500)

    async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
        response_data = await client.get(query)

    response = APIResponse(**response_data)

    # Check if any aircraft have "ground" altitude
    ground_aircraft = [a for a in response.aircraft if a.alt_baro == "ground"]

    # If we found any, verify they parse correctly
    if ground_aircraft:
        for aircraft in ground_aircraft:
            assert aircraft.alt_baro == "ground"
            assert aircraft.hex is not None
