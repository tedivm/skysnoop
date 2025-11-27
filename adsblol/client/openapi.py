"""OpenAPI client for adsb.lol API.

This module provides the OpenAPIClient class for accessing the adsb.lol
OpenAPI v2 and v0 endpoints. Unlike the re-api client, this works globally
without requiring feeder IP restrictions.
"""

import os
from logging import getLogger
from typing import Any

import httpx

from adsblol import __version__
from adsblol.client.openapi_version import OPENAPI_VERSION, SPEC_UPDATED
from adsblol.exceptions import (APIError, AuthenticationError,
                                OpenAPIValidationError, RateLimitError)
from adsblol.exceptions import TimeoutError as ADSBTimeoutError
from adsblol.models.openapi import V2ResponseModel

logger = getLogger(__name__)


class V2Methods:
    """Methods for OpenAPI v2 endpoints.

    Provides access to all v2 aircraft query endpoints. All methods return
    typed V2ResponseModel instances parsed from the API responses.
    """

    def __init__(self, client: "OpenAPIClient"):
        """Initialize V2Methods.

        Args:
            client: Parent OpenAPIClient instance
        """
        self._client = client

    async def get_pia(self) -> V2ResponseModel:
        """Get all aircraft with PIA (Privacy ICAO Address) flag.

        Returns:
            V2ResponseModel with PIA aircraft data

        Raises:
            APIError: If the request fails
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2("/v2/pia")

    async def get_mil(self) -> V2ResponseModel:
        """Get all military aircraft.

        Returns:
            V2ResponseModel with military aircraft data

        Raises:
            APIError: If the request fails
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2("/v2/mil")

    async def get_ladd(self) -> V2ResponseModel:
        """Get all LADD (Limiting Aircraft Data Displayed) aircraft.

        Returns:
            V2ResponseModel with LADD aircraft data

        Raises:
            APIError: If the request fails
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2("/v2/ladd")

    async def get_by_squawk(self, squawk: str) -> V2ResponseModel:
        """Get aircraft by squawk code.

        Args:
            squawk: Squawk code (e.g., "7700")

        Returns:
            V2ResponseModel with matching aircraft

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If squawk code is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/sqk/{squawk}")

    async def get_by_type(self, aircraft_type: str) -> V2ResponseModel:
        """Get aircraft by type designator.

        Args:
            aircraft_type: Aircraft type designator (e.g., "B738", "A320")

        Returns:
            V2ResponseModel with matching aircraft

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If type is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/type/{aircraft_type}")

    async def get_by_registration(self, registration: str) -> V2ResponseModel:
        """Get aircraft by registration.

        Args:
            registration: Aircraft registration (e.g., "N12345")

        Returns:
            V2ResponseModel with matching aircraft

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If registration is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/reg/{registration}")

    async def get_by_hex(self, icao_hex: str) -> V2ResponseModel:
        """Get aircraft by ICAO hex code.

        Args:
            icao_hex: ICAO hex code (e.g., "a1b2c3")

        Returns:
            V2ResponseModel with matching aircraft

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If hex code is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/hex/{icao_hex}")

    async def get_by_callsign(self, callsign: str) -> V2ResponseModel:
        """Get aircraft by callsign.

        Args:
            callsign: Aircraft callsign (e.g., "UAL123")

        Returns:
            V2ResponseModel with matching aircraft

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If callsign is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/callsign/{callsign}")

    async def get_by_point(self, lat: float, lon: float, radius: int) -> V2ResponseModel:
        """Get aircraft within radius of a point.

        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)
            radius: Radius in nautical miles

        Returns:
            V2ResponseModel with aircraft within radius

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If coordinates or radius are invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/point/{lat}/{lon}/{radius}")

    async def get_closest(self, lat: float, lon: float, radius: int) -> V2ResponseModel:
        """Get closest aircraft to a point within radius.

        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)
            radius: Radius in nautical miles

        Returns:
            V2ResponseModel with closest aircraft within radius

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If coordinates or radius are invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v2(f"/v2/closest/{lat}/{lon}/{radius}")


class V0Methods:
    """Methods for OpenAPI v0 endpoints.

    Provides access to v0 utility endpoints. These return dict responses
    as they have varying schemas.
    """

    def __init__(self, client: "OpenAPIClient"):
        """Initialize V0Methods.

        Args:
            client: Parent OpenAPIClient instance
        """
        self._client = client

    async def get_airport(self, icao: str) -> dict[str, Any]:
        """Get airport information by ICAO code.

        Args:
            icao: Airport ICAO code (e.g., "KSFO")

        Returns:
            dict with airport information

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If ICAO code is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v0(f"/v0/airport/{icao}")

    async def get_routes(self, planes: list[dict[str, Any]]) -> dict[str, Any]:
        """Get route information for aircraft (POST endpoint).

        Args:
            planes: List of plane dictionaries with callsign, lat, lng

        Returns:
            dict with route information

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: If plane data is invalid
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v0_post("/v0/routes", json_data={"planes": planes})

    async def get_me(self) -> dict[str, Any]:
        """Get information about the authenticated user/API key.

        Returns:
            dict with user information

        Raises:
            APIError: If the request fails
            AuthenticationError: If not authenticated
            ADSBTimeoutError: If the request times out
        """
        return await self._client._request_v0("/v0/me")


class OpenAPIClient:
    """Client for adsb.lol OpenAPI.

    Provides access to both v2 and v0 API endpoints. Works globally without
    requiring feeder IP restrictions. Will require API keys in the future.

    Example:
        async with OpenAPIClient() as client:
            # Get military aircraft
            response = await client.v2.get_mil()
            print(f"Found {response.total} military aircraft")

            # Get aircraft by hex code
            response = await client.v2.get_by_hex("a1b2c3")

            # Get closest aircraft to coordinates
            response = await client.v2.get_closest(lat=37.7749, lon=-122.4194, radius=100)
    """

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.adsb.lol", timeout: float = 30.0):
        """Initialize the OpenAPI client.

        Args:
            api_key: Optional API key (or use ADSBLOL_API_KEY env var)
            base_url: Base URL for the API (default: "https://api.adsb.lol")
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key or os.getenv("ADSBLOL_API_KEY")
        self._client: httpx.AsyncClient | None = None

        # Initialize versioned method groups
        self.v2 = V2Methods(self)
        self.v0 = V0Methods(self)

        # Log client initialization with version info
        logger.info(f"OpenAPIClient initialized (spec version: {OPENAPI_VERSION}, updated: {SPEC_UPDATED})")

    async def __aenter__(self) -> "OpenAPIClient":
        """Enter async context manager."""
        headers = {"User-Agent": f"adsblol/{__version__}"}

        # Add API key if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request_v2(self, path: str) -> V2ResponseModel:
        """Make a GET request to a v2 endpoint.

        Args:
            path: API endpoint path (e.g., "/v2/mil")

        Returns:
            Parsed V2ResponseModel

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: For 422 validation errors
            AuthenticationError: For 401 authentication errors
            RateLimitError: For 429 rate limit errors
            ADSBTimeoutError: If the request times out
        """
        data = await self._request("GET", path)
        return V2ResponseModel.model_validate(data)

    async def _request_v0(self, path: str) -> dict[str, Any]:
        """Make a GET request to a v0 endpoint.

        Args:
            path: API endpoint path (e.g., "/v0/airport/KSFO")

        Returns:
            Response JSON as dict

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: For 422 validation errors
            AuthenticationError: For 401 authentication errors
            RateLimitError: For 429 rate limit errors
            ADSBTimeoutError: If the request times out
        """
        return await self._request("GET", path)

    async def _request_v0_post(self, path: str, json_data: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request to a v0 endpoint.

        Args:
            path: API endpoint path (e.g., "/v0/routes")
            json_data: JSON data to send in request body

        Returns:
            Response JSON as dict

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: For 422 validation errors
            AuthenticationError: For 401 authentication errors
            RateLimitError: For 429 rate limit errors
            ADSBTimeoutError: If the request times out
        """
        return await self._request("POST", path, json_data=json_data)

    async def _request(self, method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an HTTP request to the OpenAPI.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path
            json_data: Optional JSON data for POST requests

        Returns:
            Response JSON as dict

        Raises:
            APIError: If the request fails
            OpenAPIValidationError: For 422 validation errors
            AuthenticationError: For 401 authentication errors
            RateLimitError: For 429 rate limit errors
            ADSBTimeoutError: If the request times out
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        url = f"{self.base_url}{path}"
        logger.debug(f"{method} request to: {url}")

        try:
            if method == "GET":
                response = await self._client.get(url)
            elif method == "POST":
                response = await self._client.post(url, json=json_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle different status codes
            if response.status_code == 422:
                # Validation error - parse error details
                try:
                    error_data = response.json()
                    details = error_data.get("detail", [])
                    raise OpenAPIValidationError(
                        message=f"Validation error: {response.text}",
                        details=details,
                        status_code=422,
                    )
                except ValueError:
                    # Couldn't parse JSON, raise generic error
                    raise OpenAPIValidationError(
                        message=f"Validation error: {response.text}",
                        status_code=422,
                    )

            elif response.status_code == 401:
                raise AuthenticationError("Authentication failed. Invalid or missing API key.")

            elif response.status_code == 429:
                # Rate limit error - extract retry-after if available
                retry_after = None
                if "Retry-After" in response.headers:
                    try:
                        retry_after = int(response.headers["Retry-After"])
                    except ValueError:
                        pass
                raise RateLimitError(
                    message=f"Rate limit exceeded: {response.text}",
                    retry_after=retry_after,
                )

            # Raise for other error status codes
            response.raise_for_status()

            # Parse and return JSON
            data = response.json()
            logger.debug(f"Response received: {data.get('total', 'unknown')} aircraft")
            return data

        except httpx.TimeoutException as e:
            logger.exception(f"Request timeout: {e}")
            raise ADSBTimeoutError(f"Request timed out after {self.timeout} seconds") from e

        except httpx.HTTPStatusError as e:
            # This catches errors not handled above
            logger.exception(f"HTTP error {e.response.status_code}: {e}")
            raise APIError(f"API request failed with status {e.response.status_code}: {e.response.text}") from e

        except httpx.RequestError as e:
            logger.exception(f"Request error: {e}")
            raise APIError(f"API request failed: {str(e)}") from e

        except ValueError as e:
            logger.exception(f"Invalid JSON response: {e}")
            raise APIError(f"Invalid JSON response from API: {str(e)}") from e
