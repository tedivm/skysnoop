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
        help="Run tests that require access to the live adsb.lol re-api (feeder-only)",
    )
    parser.addoption(
        "--run-live-openapi",
        action="store_true",
        default=False,
        help="Run tests that require access to the live adsb.lol OpenAPI (globally accessible)",
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

    for item in items:
        if "live_api" in item.keywords and not run_live_api:
            item.add_marker(skip_live_api)
        if "live_openapi" in item.keywords and not run_live_openapi:
            item.add_marker(skip_live_openapi)
