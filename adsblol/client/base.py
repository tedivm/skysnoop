"""Base HTTP client for adsb.lol API communication.

This module provides the BaseHTTPClient class that handles low-level HTTP
communication with the adsb.lol API using httpx.
"""

from logging import getLogger
from typing import Any

import httpx

from adsblol import __version__
from adsblol.exceptions import APIError
from adsblol.exceptions import TimeoutError as ADSBTimeoutError

logger = getLogger(__name__)


class BaseHTTPClient:
    """Base HTTP client for adsb.lol API.

    Wraps httpx.AsyncClient to provide a simple interface for making API requests.
    Handles URL construction, error handling, and resource cleanup.

    CRITICAL: Query strings must be pre-formatted and passed directly to avoid
    httpx URL-encoding commas, which would break the API.

    Example:
        async with BaseHTTPClient(base_url="https://re-api.adsb.lol/") as client:
            # CORRECT: Pass pre-formatted query string
            response = await client.get("circle=37.7,-122.4,100")

            # WRONG: Don't use params dict - httpx will encode commas
            # response = await client.get(params={"circle": "37.7,-122.4,100"})
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for the API (e.g., "https://re-api.adsb.lol/")
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash if present
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BaseHTTPClient":
        """Enter async context manager."""
        # Set user agent header with project name and version
        headers = {"User-Agent": f"adsblol/{__version__}"}

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers,
            follow_redirects=True,  # Follow redirects automatically
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get(self, query_string: str) -> dict[str, Any]:
        """Make a GET request to the API.

        Args:
            query_string: Pre-formatted query string (e.g., "circle=37.7,-122.4,100")
                         Do NOT pass a dict - commas must not be URL-encoded

        Returns:
            Response JSON as a dictionary

        Raises:
            APIError: If the request fails or returns an error status
            ADSBTimeoutError: If the request times out
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        # Construct URL manually to preserve commas
        url = f"{self.base_url}?{query_string}"

        logger.debug(f"GET request to: {url}")

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Response received: {len(data.get('aircraft', []))} aircraft")
            return data

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise ADSBTimeoutError(f"Request timed out after {self.timeout} seconds") from e

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise APIError(f"API request failed with status {e.response.status_code}: {e.response.text}") from e

        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise APIError(f"API request failed: {str(e)}") from e

        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise APIError(f"Invalid JSON response from API: {str(e)}") from e
            raise APIError(f"Invalid JSON response from API: {str(e)}") from e
