"""Shared protocol compliance test suite for backend adapters.

This module provides a reusable test suite that validates BackendProtocol
compliance for all adapter implementations. Tests are parameterized to run
against different adapter instances.
"""

import pytest

from skysnoop.models import SkyData


class BaseProtocolTestSuite:
    """Shared test suite for BackendProtocol compliance.

    This class defines tests that all backend adapters must pass. Test classes
    should inherit from this and provide a fixture that returns an adapter instance.

    Example:
        class TestMyAdapter(BaseProtocolTestSuite):
            @pytest.fixture
            async def adapter(self):
                async with MyAdapter() as adapter:
                    yield adapter
    """

    @pytest.fixture
    def adapter(self):
        """Override this fixture to provide adapter instance.

        Yields:
            Adapter instance implementing BackendProtocol
        """
        pytest.skip("Adapter fixture must be implemented by subclass")

    @pytest.mark.asyncio
    async def test_implements_protocol(self, adapter):
        """Test adapter implements BackendProtocol."""
        # Check that adapter has all required methods
        assert hasattr(adapter, "get_by_hex")
        assert hasattr(adapter, "get_by_callsign")
        assert hasattr(adapter, "get_by_registration")
        assert hasattr(adapter, "get_by_type")
        assert hasattr(adapter, "get_in_circle")
        assert hasattr(adapter, "get_closest")
        assert hasattr(adapter, "get_in_box")
        assert hasattr(adapter, "get_all_with_pos")
        assert hasattr(adapter, "__aenter__")
        assert hasattr(adapter, "__aexit__")

    @pytest.mark.asyncio
    async def test_get_by_hex_returns_skydata(self, adapter):
        """Test get_by_hex returns SkyData instance."""
        result = await adapter.get_by_hex("abc123")
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "result_count")

    @pytest.mark.asyncio
    async def test_get_by_callsign_returns_skydata(self, adapter):
        """Test get_by_callsign returns SkyData instance."""
        result = await adapter.get_by_callsign("TEST123")
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_get_by_registration_returns_skydata(self, adapter):
        """Test get_by_registration returns SkyData instance."""
        result = await adapter.get_by_registration("N12345")
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_get_by_type_returns_skydata(self, adapter):
        """Test get_by_type returns SkyData instance."""
        result = await adapter.get_by_type("B738")
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_get_in_circle_returns_skydata(self, adapter):
        """Test get_in_circle returns SkyData instance."""
        result = await adapter.get_in_circle(lat=37.7749, lon=-122.4194, radius=50.0)
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_get_closest_returns_skydata(self, adapter):
        """Test get_closest returns SkyData instance."""
        result = await adapter.get_closest(lat=37.7749, lon=-122.4194, radius=50.0)
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_get_in_box_returns_skydata(self, adapter):
        """Test get_in_box returns SkyData instance."""
        result = await adapter.get_in_box(
            lat_south=37.0,
            lat_north=38.0,
            lon_west=-123.0,
            lon_east=-122.0,
        )
        assert isinstance(result, SkyData)
        assert hasattr(result, "aircraft")
        assert hasattr(result, "backend")

    @pytest.mark.asyncio
    async def test_context_manager_support(self, adapter):
        """Test adapter supports async context manager protocol."""
        # Adapter fixture should have already entered context
        # Just verify it has the methods
        assert callable(getattr(adapter, "__aenter__", None))
        assert callable(getattr(adapter, "__aexit__", None))

    @pytest.mark.asyncio
    async def test_skydata_has_correct_backend_field(self, adapter):
        """Test SkyData response has correct backend field."""
        result = await adapter.get_by_hex("abc123")
        assert result.backend in ["openapi", "reapi"]

    @pytest.mark.asyncio
    async def test_skydata_has_timestamp(self, adapter):
        """Test SkyData response has timestamp field."""
        result = await adapter.get_by_hex("abc123")
        assert isinstance(result.timestamp, float)
        assert result.timestamp > 0

    @pytest.mark.asyncio
    async def test_skydata_has_result_count(self, adapter):
        """Test SkyData response has result_count field."""
        result = await adapter.get_by_hex("abc123")
        assert isinstance(result.result_count, int)
        assert result.result_count >= 0

    @pytest.mark.asyncio
    async def test_skydata_aircraft_list(self, adapter):
        """Test SkyData response has aircraft list."""
        result = await adapter.get_by_hex("abc123")
        assert isinstance(result.aircraft, list)
        assert len(result.aircraft) == result.result_count

    @pytest.mark.asyncio
    async def test_convenience_properties(self, adapter):
        """Test SkyData convenience properties work correctly."""
        result = await adapter.get_by_hex("abc123")
        assert result.count == result.result_count
        assert result.has_results == (result.result_count > 0)
        assert len(result) == len(result.aircraft)
