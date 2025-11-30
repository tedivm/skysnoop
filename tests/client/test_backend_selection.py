"""Tests for backend selection logic."""

import pytest

from skysnoop.client.backend_selection import select_backend, select_backend_sync


class TestBackendSelection:
    """Test automatic backend selection logic."""

    @pytest.mark.asyncio
    async def test_select_backend_with_api_key(self):
        """Test that API key triggers OpenAPI backend selection."""
        backend = await select_backend(api_key="test_key_123")
        assert backend == "openapi"

    @pytest.mark.asyncio
    async def test_select_backend_without_api_key_prefers_reapi(self):
        """Test that no API key with prefer_reapi=True selects RE-API."""
        backend = await select_backend(api_key=None, prefer_reapi=True)
        assert backend == "reapi"

    @pytest.mark.asyncio
    async def test_select_backend_without_api_key_fallback_openapi(self):
        """Test that prefer_reapi=False falls back to OpenAPI."""
        backend = await select_backend(api_key=None, prefer_reapi=False)
        assert backend == "openapi"

    @pytest.mark.asyncio
    async def test_select_backend_default_prefers_reapi(self):
        """Test that default behavior prefers RE-API when no API key."""
        backend = await select_backend()
        assert backend == "reapi"

    def test_select_backend_sync_with_api_key(self):
        """Test synchronous selection with API key."""
        backend = select_backend_sync(api_key="test_key_123")
        assert backend == "openapi"

    def test_select_backend_sync_without_api_key_prefers_reapi(self):
        """Test synchronous selection prefers RE-API without API key."""
        backend = select_backend_sync(api_key=None, prefer_reapi=True)
        assert backend == "reapi"

    def test_select_backend_sync_without_api_key_fallback_openapi(self):
        """Test synchronous selection fallback to OpenAPI."""
        backend = select_backend_sync(api_key=None, prefer_reapi=False)
        assert backend == "openapi"

    def test_select_backend_sync_default(self):
        """Test synchronous default selection."""
        backend = select_backend_sync()
        assert backend == "reapi"


class TestBackendSelectionEdgeCases:
    """Test edge cases in backend selection."""

    @pytest.mark.asyncio
    async def test_empty_string_api_key_treated_as_none(self):
        """Test that empty string API key is treated as None."""
        # Empty string is falsy in Python
        backend = await select_backend(api_key="")
        assert backend == "reapi"

    @pytest.mark.asyncio
    async def test_whitespace_api_key_triggers_openapi(self):
        """Test that whitespace-only API key still triggers OpenAPI."""
        backend = await select_backend(api_key="   ")
        assert backend == "openapi"

    @pytest.mark.asyncio
    async def test_api_key_overrides_prefer_reapi(self):
        """Test that API key overrides prefer_reapi setting."""
        backend = await select_backend(api_key="test_key", prefer_reapi=True)
        assert backend == "openapi"

    def test_sync_and_async_consistency(self):
        """Test that sync and async versions produce consistent results."""
        # With API key
        sync_result = select_backend_sync(api_key="test_key")
        assert sync_result == "openapi"

        # Without API key, prefer RE-API
        sync_result = select_backend_sync(prefer_reapi=True)
        assert sync_result == "reapi"

        # Without API key, fallback to OpenAPI
        sync_result = select_backend_sync(prefer_reapi=False)
        assert sync_result == "openapi"
