"""Integration tests for SkySnoop with live APIs.

These tests are optional and run against real API endpoints.

To run RE-API tests:
    pytest tests/integration/test_skysnoop_live.py::TestSkySnoopLiveReAPI -v --run-live-api

To run OpenAPI tests:
    pytest tests/integration/test_skysnoop_live.py::TestSkySnoopLiveOpenAPI -v --run-live-openapi
"""

import pytest

from skysnoop.client.skysnoop import SkySnoop
from skysnoop.exceptions import UnsupportedOperationError


@pytest.mark.live_api
class TestSkySnoopLiveReAPI:
    """Integration tests with live RE-API backend."""

    @pytest.mark.asyncio
    async def test_reapi_get_by_hex_live(self):
        """Test get_by_hex with live RE-API."""
        async with SkySnoop(backend="reapi") as client:
            # Use a known active aircraft hex code (this may fail if aircraft not flying)
            # Using a popular aircraft type's hex for better chance of results
            result = await client.get_by_hex("a12345")

            # Verify response structure (may be empty if aircraft not flying)
            assert result.backend == "reapi"
            assert result.timestamp > 0
            assert result.result_count >= 0
            assert not result.simulated

    @pytest.mark.asyncio
    async def test_reapi_get_in_circle_live(self):
        """Test get_in_circle with live RE-API near a major airport."""
        async with SkySnoop(backend="reapi") as client:
            # Search near San Francisco International Airport
            result = await client.get_in_circle(
                lat=37.6213,
                lon=-122.3790,
                radius=10,
            )

            assert result.backend == "reapi"
            assert result.timestamp > 0
            assert not result.simulated
            # Results may vary, but structure should be valid
            assert isinstance(result.result_count, int)

    @pytest.mark.asyncio
    async def test_reapi_get_in_box_live(self):
        """Test get_in_box with live RE-API (native support)."""
        async with SkySnoop(backend="reapi") as client:
            # Small box around San Francisco Bay Area
            result = await client.get_in_box(
                lat_min=37.5,
                lat_max=37.8,
                lon_min=-122.5,
                lon_max=-122.3,
            )

            assert result.backend == "reapi"
            assert not result.simulated  # Native box query support
            assert result.timestamp > 0

    @pytest.mark.asyncio
    async def test_reapi_get_all_with_pos_live(self):
        """Test get_all_with_pos with live RE-API (may return many results)."""
        async with SkySnoop(backend="reapi") as client:
            result = await client.get_all_with_pos()

            assert result.backend == "reapi"
            assert not result.simulated
            assert result.timestamp > 0
            # Should return many aircraft with position data
            assert result.result_count > 0


@pytest.mark.live_openapi
class TestSkySnoopLiveOpenAPI:
    """Integration tests with live OpenAPI backend."""

    @pytest.mark.asyncio
    async def test_openapi_get_by_hex_live(self):
        """Test get_by_hex with live OpenAPI."""
        async with SkySnoop(backend="openapi") as client:
            result = await client.get_by_hex("a12345")

            assert result.backend == "openapi"
            assert result.timestamp > 0
            assert result.result_count >= 0
            assert not result.simulated  # Direct lookup, not simulated

    @pytest.mark.asyncio
    async def test_openapi_get_in_circle_live(self):
        """Test get_in_circle with live OpenAPI near major airport."""
        async with SkySnoop(backend="openapi") as client:
            # Search near LAX
            result = await client.get_in_circle(
                lat=33.9416,
                lon=-118.4085,
                radius=10,
            )

            assert result.backend == "openapi"
            assert result.timestamp > 0
            assert not result.simulated  # Native circle support

    @pytest.mark.asyncio
    async def test_openapi_get_in_box_live_simulated(self):
        """Test get_in_box with live OpenAPI (simulated via circle)."""
        async with SkySnoop(backend="openapi") as client:
            # Small box around Los Angeles area
            result = await client.get_in_box(
                lat_min=33.8,
                lat_max=34.1,
                lon_min=-118.5,
                lon_max=-118.2,
            )

            assert result.backend == "openapi"
            assert result.simulated  # Box query simulated
            assert result.timestamp > 0

    @pytest.mark.asyncio
    async def test_openapi_get_all_with_pos_raises_error(self):
        """Test that get_all_with_pos raises error with OpenAPI."""
        async with SkySnoop(backend="openapi") as client:
            with pytest.raises(UnsupportedOperationError, match="not supported"):
                await client.get_all_with_pos()


class TestSkySnoopLiveAutoBackend:
    """Integration tests with auto backend selection."""

    @pytest.mark.asyncio
    @pytest.mark.live_api
    async def test_auto_backend_defaults_to_reapi(self):
        """Test that auto backend selection defaults to RE-API."""
        async with SkySnoop(backend="auto") as client:
            result = await client.get_in_circle(
                lat=40.7128,
                lon=-74.0060,
                radius=15,
            )

            # Should use RE-API by default (preferred)
            assert result.backend == "reapi"
            assert not result.simulated

    @pytest.mark.asyncio
    @pytest.mark.live_openapi
    async def test_auto_backend_with_api_key_uses_openapi(self):
        """Test that API key triggers OpenAPI backend."""
        async with SkySnoop(backend="auto", api_key="test_key") as client:
            result = await client.get_in_circle(
                lat=40.7128,
                lon=-74.0060,
                radius=15,
            )

            # Should use OpenAPI when API key provided
            assert result.backend == "openapi"

    @pytest.mark.asyncio
    @pytest.mark.live_api
    @pytest.mark.live_openapi
    async def test_backend_switching_behavior(self):
        """Test that different backends can be used for same query."""
        # Query near Chicago O'Hare
        lat, lon, radius = 41.9742, -87.9073, 10

        # Get results from both backends
        async with SkySnoop(backend="reapi") as reapi_client:
            reapi_result = await reapi_client.get_in_circle(lat, lon, radius)

        async with SkySnoop(backend="openapi") as openapi_client:
            openapi_result = await openapi_client.get_in_circle(lat, lon, radius)

        # Both should work and return valid responses
        assert reapi_result.backend == "reapi"
        assert openapi_result.backend == "openapi"
        assert reapi_result.timestamp > 0
        assert openapi_result.timestamp > 0

        # Results may differ slightly due to timing, but both should be valid
        assert isinstance(reapi_result.result_count, int)
        assert isinstance(openapi_result.result_count, int)


class TestSkySnoopLiveFilters:
    """Integration tests for QueryFilters."""

    @pytest.mark.asyncio
    @pytest.mark.live_api
    async def test_filters_with_reapi_circle(self):
        """Test QueryFilters work with RE-API circle query."""
        from skysnoop.query.filters import QueryFilters

        async with SkySnoop(backend="reapi") as client:
            filters = QueryFilters(military=True)
            result = await client.get_in_circle(
                lat=38.8977,
                lon=-77.0365,  # Near Washington DC
                radius=50,
                filters=filters,
            )

            assert result.backend == "reapi"
            # May or may not have results, but should not error
            assert result.result_count >= 0

    @pytest.mark.asyncio
    @pytest.mark.live_openapi
    async def test_filters_ignored_with_openapi(self):
        """Test that filters are ignored (with warning) on OpenAPI."""
        from skysnoop.query.filters import QueryFilters

        async with SkySnoop(backend="openapi") as client:
            filters = QueryFilters(military=True)
            # Should work but ignore filters (logs warning)
            result = await client.get_in_circle(
                lat=38.8977,
                lon=-77.0365,
                radius=50,
                filters=filters,
            )

            assert result.backend == "openapi"
            assert result.result_count >= 0
