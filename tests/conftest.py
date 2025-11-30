"""Shared test fixtures and configuration."""

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def api_responses_dir(fixtures_dir: Path) -> Path:
    """Return the path to the API responses fixtures directory."""
    return fixtures_dir / "api_responses"


@pytest.fixture
def load_api_response(api_responses_dir: Path):
    """Load an API response fixture from a JSON file.

    Returns:
        A function that accepts a filename and returns the parsed JSON data.
    """

    def _load(filename: str) -> dict[str, Any]:
        """Load and parse a JSON fixture file.

        Args:
            filename: Name of the JSON file in the api_responses directory

        Returns:
            Parsed JSON data as a dictionary
        """
        filepath = api_responses_dir / filename
        with open(filepath) as f:
            return json.load(f)

    return _load


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-live-api",
        action="store_true",
        default=False,
        help="Run tests that require access to the live adsb.lol re-api (feeder-only). Includes RE-API backend tests and RE-API integration tests.",
    )
    parser.addoption(
        "--run-live-openapi",
        action="store_true",
        default=False,
        help="Run tests that require access to the live adsb.lol OpenAPI (globally accessible). Includes OpenAPI backend tests and OpenAPI integration tests.",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "live_api: marks tests that require access to the live adsb.lol re-api (feeder-only)",
    )
    config.addinivalue_line(
        "markers",
        "live_openapi: marks tests that require access to the live adsb.lol OpenAPI (globally accessible)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip live_api and live_openapi tests unless respective flags are specified."""
    run_live_api = config.getoption("--run-live-api")
    run_live_openapi = config.getoption("--run-live-openapi")

    skip_live_api = pytest.mark.skip(reason="need --run-live-api option to run")
    skip_live_openapi = pytest.mark.skip(reason="need --run-live-openapi option to run")
    skip_both = pytest.mark.skip(reason="need both --run-live-api and --run-live-openapi options to run")

    for item in items:
        has_live_api = "live_api" in item.keywords
        has_live_openapi = "live_openapi" in item.keywords

        # If a test has both markers, require both flags
        if has_live_api and has_live_openapi:
            if not (run_live_api and run_live_openapi):
                item.add_marker(skip_both)
        # If test has only live_api marker
        elif has_live_api and not run_live_api:
            item.add_marker(skip_live_api)
        # If test has only live_openapi marker
        elif has_live_openapi and not run_live_openapi:
            item.add_marker(skip_live_openapi)


# OpenAPI response fixtures


@pytest.fixture
def openapi_responses_dir(fixtures_dir: Path) -> Path:
    """Return the path to the OpenAPI responses fixtures directory."""
    return fixtures_dir / "openapi_responses"


@pytest.fixture
def load_openapi_response(openapi_responses_dir: Path):
    """Load an OpenAPI response fixture from a JSON file.

    Returns:
        A function that accepts a filename and returns the parsed JSON data.
    """

    def _load(filename: str) -> dict[str, Any]:
        """Load and parse a JSON fixture file.

        Args:
            filename: Name of the JSON file in the openapi_responses directory

        Returns:
            Parsed JSON data as a dictionary
        """
        filepath = openapi_responses_dir / filename
        with open(filepath) as f:
            return json.load(f)

    return _load


# SkySnoop unified client fixtures


@pytest.fixture
def mock_skydata():
    """Create a mock SkyData instance for testing.

    Returns:
        A function that creates SkyData with customizable parameters.
    """
    from skysnoop.models.skydata import SkyData

    def _create(
        backend: str = "reapi",
        result_count: int = 1,
        simulated: bool = False,
        aircraft: list | None = None,
    ) -> SkyData:
        """Create a SkyData instance with test data.

        Args:
            backend: Backend type ("openapi" or "reapi")
            result_count: Number of aircraft in results
            simulated: Whether operation was simulated
            aircraft: List of Aircraft objects (empty list if None)

        Returns:
            SkyData instance for testing
        """
        if aircraft is None:
            aircraft = []

        return SkyData(
            timestamp=1704067200.0,  # 2024-01-01 00:00:00 UTC
            result_count=result_count,
            aircraft=aircraft,
            backend=backend,
            simulated=simulated,
        )

    return _create


@pytest.fixture
def mock_aircraft():
    """Create a mock Aircraft instance for testing.

    Returns:
        A function that creates Aircraft with customizable parameters.
    """
    from skysnoop.models.aircraft import Aircraft

    def _create(
        hex_code: str = "abc123",
        callsign: str | None = "TEST123",
        registration: str | None = "N12345",
        aircraft_type: str | None = "B738",
        lat: float | None = 37.7749,
        lon: float | None = -122.4194,
        alt_baro: int | None = 35000,
    ) -> Aircraft:
        """Create an Aircraft instance with test data.

        Args:
            hex_code: ICAO 24-bit hex code
            callsign: Aircraft callsign
            registration: Aircraft registration
            aircraft_type: Aircraft type code
            lat: Latitude
            lon: Longitude
            alt_baro: Barometric altitude in feet

        Returns:
            Aircraft instance for testing
        """
        return Aircraft(
            hex=hex_code,
            callsign=callsign,
            registration=registration,
            type=aircraft_type,
            lat=lat,
            lon=lon,
            alt_baro=alt_baro,
        )

    return _create


# CLI test fixtures for SkyData responses


@pytest.fixture
def skydata_response(mock_skydata, mock_aircraft):
    """Create a SkyData response with multiple aircraft for CLI testing."""
    aircraft_list = [
        mock_aircraft(hex_code="abc123", callsign="TEST123", alt_baro=35000),
        mock_aircraft(hex_code="def456", callsign="TEST456", alt_baro=28000),
    ]
    return mock_skydata(result_count=len(aircraft_list), aircraft=aircraft_list)


@pytest.fixture
def empty_skydata_response(mock_skydata):
    """Create an empty SkyData response for CLI testing."""
    return mock_skydata(result_count=0, aircraft=[])


@pytest.fixture
def single_skydata_response(mock_skydata, mock_aircraft):
    """Create a SkyData response with a single aircraft for CLI testing."""
    aircraft_list = [mock_aircraft(hex_code="abc123", callsign="TEST123", alt_baro=35000)]
    return mock_skydata(result_count=1, aircraft=aircraft_list)
