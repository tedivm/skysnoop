"""Tests for SkySnoop unified client."""

from unittest.mock import AsyncMock, patch

import pytest

from skysnoop.client.skysnoop import SkySnoop
from skysnoop.exceptions import UnsupportedOperationError
from skysnoop.models.skydata import SkyData


class TestSkySnoopInitialization:
    """Test SkySnoop client initialization."""

    def test_default_initialization(self):
        """Test default initialization selects RE-API backend."""
        client = SkySnoop()
        assert client.backend_type == "reapi"
        assert client._adapter is None  # Not initialized until context manager

    def test_explicit_reapi_backend(self):
        """Test explicit RE-API backend selection."""
        client = SkySnoop(backend="reapi")
        assert client.backend_type == "reapi"

    def test_explicit_openapi_backend(self):
        """Test explicit OpenAPI backend selection."""
        client = SkySnoop(backend="openapi")
        assert client.backend_type == "openapi"

    def test_auto_backend_with_api_key(self):
        """Test auto backend selection with API key triggers OpenAPI."""
        client = SkySnoop(backend="auto", api_key="test_key")
        assert client.backend_type == "openapi"

    def test_auto_backend_without_api_key(self):
        """Test auto backend selection without API key selects RE-API."""
        client = SkySnoop(backend="auto")
        assert client.backend_type == "reapi"

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Invalid backend"):
            SkySnoop(backend="invalid")  # type: ignore

    def test_api_key_stored(self):
        """Test that API key is stored for adapter initialization."""
        client = SkySnoop(api_key="test_key_123")
        assert client._api_key == "test_key_123"

    def test_base_url_stored(self):
        """Test that base URL is stored for adapter initialization."""
        client = SkySnoop(base_url="https://custom.api.com")
        assert client._base_url == "https://custom.api.com"

    def test_timeout_stored(self):
        """Test that timeout is stored for adapter initialization."""
        client = SkySnoop(timeout=60.0)
        assert client._timeout == 60.0


class TestSkySnoopContextManager:
    """Test SkySnoop async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_initializes_reapi_adapter(self):
        """Test that context manager initializes RE-API adapter."""
        client = SkySnoop(backend="reapi")

        async with client:
            assert client._adapter is not None
            # Adapter should be ReAPIAdapter (we'll check via duck typing)
            assert hasattr(client._adapter, "get_by_hex")

        # After exiting, adapter should be None
        assert client._adapter is None

    @pytest.mark.asyncio
    async def test_context_manager_initializes_openapi_adapter(self):
        """Test that context manager initializes OpenAPI adapter."""
        client = SkySnoop(backend="openapi")

        async with client:
            assert client._adapter is not None
            assert hasattr(client._adapter, "get_by_hex")

        assert client._adapter is None

    @pytest.mark.asyncio
    async def test_context_manager_passes_parameters_to_openapi_adapter(self):
        """Test that context manager passes parameters to OpenAPI adapter."""
        with patch("skysnoop.client.skysnoop.OpenAPIAdapter") as MockAdapter:
            mock_adapter_instance = AsyncMock()
            MockAdapter.return_value = mock_adapter_instance

            client = SkySnoop(
                backend="openapi",
                api_key="test_key",
                base_url="https://custom.api.com",
                timeout=60.0,
            )

            async with client:
                pass

            # Verify OpenAPIAdapter was called with correct parameters
            MockAdapter.assert_called_once_with(
                api_key="test_key",
                base_url="https://custom.api.com",
                timeout=60.0,
            )

    @pytest.mark.asyncio
    async def test_context_manager_passes_parameters_to_reapi_adapter(self):
        """Test that context manager passes parameters to RE-API adapter."""
        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter_instance = AsyncMock()
            MockAdapter.return_value = mock_adapter_instance

            client = SkySnoop(
                backend="reapi",
                base_url="https://custom.re-api.com",
                timeout=45.0,
            )

            async with client:
                pass

            # Verify ReAPIAdapter was called with correct parameters
            MockAdapter.assert_called_once_with(
                base_url="https://custom.re-api.com",
                timeout=45.0,
            )

    @pytest.mark.asyncio
    async def test_methods_require_context_manager(self):
        """Test that methods raise error when used outside context manager."""
        client = SkySnoop()

        with pytest.raises(RuntimeError, match="must be used as an async context manager"):
            await client.get_by_hex("abc123")


class TestSkySnoopDelegation:
    """Test SkySnoop method delegation to adapters."""

    @pytest.mark.asyncio
    async def test_get_by_hex_delegates_to_adapter(self):
        """Test get_by_hex delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=1,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_by_hex = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_by_hex("abc123")

            mock_adapter.get_by_hex.assert_called_once_with(hex_code="abc123")
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_by_callsign_delegates_to_adapter(self):
        """Test get_by_callsign delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=1,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_by_callsign = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_by_callsign("UAL123")

            mock_adapter.get_by_callsign.assert_called_once_with(callsign="UAL123")
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_by_registration_delegates_to_adapter(self):
        """Test get_by_registration delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=1,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_by_registration = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_by_registration("N12345")

            mock_adapter.get_by_registration.assert_called_once_with(registration="N12345")
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_by_type_delegates_to_adapter(self):
        """Test get_by_type delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=2,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_by_type = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_by_type("B738")

            mock_adapter.get_by_type.assert_called_once_with(aircraft_type="B738")
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_in_circle_delegates_to_adapter(self):
        """Test get_in_circle delegates to adapter with filters."""
        from skysnoop.query.filters import QueryFilters

        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=5,
            aircraft=[],
            backend="reapi",
        )
        filters = QueryFilters(military=True)

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_in_circle = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_in_circle(37.7749, -122.4194, 50, filters=filters)

            mock_adapter.get_in_circle.assert_called_once_with(
                lat=37.7749,
                lon=-122.4194,
                radius=50,
                filters=filters,
            )
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_closest_delegates_to_adapter(self):
        """Test get_closest delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=1,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_closest = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_closest(37.7749, -122.4194, 100)

            mock_adapter.get_closest.assert_called_once_with(
                lat=37.7749,
                lon=-122.4194,
                radius=100,
                filters=None,
            )
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_in_box_delegates_to_adapter(self):
        """Test get_in_box delegates to adapter."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=10,
            aircraft=[],
            backend="reapi",
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_in_box = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_in_box(37.0, 38.0, -123.0, -122.0)

            mock_adapter.get_in_box.assert_called_once_with(
                lat_south=37.0,
                lat_north=38.0,
                lon_west=-123.0,
                lon_east=-122.0,
                filters=None,
            )
            assert result == mock_skydata

    @pytest.mark.asyncio
    async def test_get_all_with_pos_delegates_to_adapter(self):
        """Test get_all_with_pos delegates to adapter."""
        from skysnoop.query.filters import QueryFilters

        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=100,
            aircraft=[],
            backend="reapi",
        )
        filters = QueryFilters(military=True)

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_all_with_pos = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_all_with_pos(filters=filters)

            mock_adapter.get_all_with_pos.assert_called_once_with(filters=filters)
            assert result == mock_skydata


class TestSkySnoopSimulationFlag:
    """Test that simulated operations are properly flagged."""

    @pytest.mark.asyncio
    async def test_openapi_box_query_returns_simulated_flag(self):
        """Test that box query with OpenAPI backend returns simulated=True."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=5,
            aircraft=[],
            backend="openapi",
            simulated=True,
        )

        with patch("skysnoop.client.skysnoop.OpenAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_in_box = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="openapi") as client:
                result = await client.get_in_box(37.0, 38.0, -123.0, -122.0)

            assert result.simulated is True
            assert result.backend == "openapi"

    @pytest.mark.asyncio
    async def test_reapi_box_query_returns_native_flag(self):
        """Test that box query with RE-API backend returns simulated=False."""
        mock_skydata = SkyData(
            timestamp=1704067200.0,
            result_count=5,
            aircraft=[],
            backend="reapi",
            simulated=False,
        )

        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_in_box = AsyncMock(return_value=mock_skydata)
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                result = await client.get_in_box(37.0, 38.0, -123.0, -122.0)

            assert result.simulated is False
            assert result.backend == "reapi"


class TestSkySnoopErrorPropagation:
    """Test error propagation from adapters."""

    @pytest.mark.asyncio
    async def test_unsupported_operation_error_propagates(self):
        """Test that UnsupportedOperationError propagates from adapter."""
        with patch("skysnoop.client.skysnoop.OpenAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_all_with_pos = AsyncMock(
                side_effect=UnsupportedOperationError("Not supported on OpenAPI backend")
            )
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="openapi") as client:
                with pytest.raises(UnsupportedOperationError, match="Not supported on OpenAPI"):
                    await client.get_all_with_pos()

    @pytest.mark.asyncio
    async def test_generic_exception_propagates(self):
        """Test that generic exceptions propagate from adapter."""
        with patch("skysnoop.client.skysnoop.ReAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.get_by_hex = AsyncMock(side_effect=ValueError("Invalid hex code"))
            MockAdapter.return_value = mock_adapter

            async with SkySnoop(backend="reapi") as client:
                with pytest.raises(ValueError, match="Invalid hex code"):
                    await client.get_by_hex("invalid")
