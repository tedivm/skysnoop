"""Tests for CLI commands."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from skysnoop.cli import app
from skysnoop.models.response import APIResponse

runner = CliRunner()


@pytest.fixture
def api_responses_dir():
    """Get path to API response fixtures directory."""
    return Path(__file__).parent / "fixtures" / "api_responses"


@pytest.fixture
def circle_response(api_responses_dir):
    """Load circle query response fixture."""
    with open(api_responses_dir / "circle_multiple_aircraft.json") as f:
        data = json.load(f)
    return APIResponse(**data)


@pytest.fixture
def single_aircraft_response(api_responses_dir):
    """Load single aircraft response fixture."""
    with open(api_responses_dir / "circle_single_aircraft.json") as f:
        data = json.load(f)
    return APIResponse(**data)


@pytest.fixture
def empty_response():
    """Create empty response fixture."""
    return APIResponse(now=1234567890.0, resultCount=0, ptime=0.01, aircraft=[])


def test_version_command():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "skysnoop" in result.stdout


@patch("skysnoop.cli.ReAPIClient")
def test_circle_command_table_output(mock_client_class, circle_response):
    """Test circle command with table output."""
    mock_client = AsyncMock()
    mock_client.circle.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    assert "aircraft" in result.stdout
    mock_client.circle.assert_called_once()


@patch("skysnoop.cli.ReAPIClient")
def test_circle_command_json_output(mock_client_class, circle_response):
    """Test circle command with JSON output."""
    mock_client = AsyncMock()
    mock_client.circle.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--json", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 0
    # Verify it's valid JSON
    output = json.loads(result.stdout)
    assert "aircraft" in output
    assert "resultCount" in output


@patch("skysnoop.cli.ReAPIClient")
def test_circle_command_with_filters(mock_client_class, circle_response):
    """Test circle command with altitude filter."""
    mock_client = AsyncMock()
    mock_client.circle.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(
        app,
        ["circle", "--type", "A321", "--above-alt", "20000", "--", "37.7749", "-122.4194", "200"],
    )

    assert result.exit_code == 0
    # Verify filters were passed
    call_args = mock_client.circle.call_args
    assert call_args.kwargs["filters"] is not None
    assert call_args.kwargs["filters"].type_code == "A321"
    assert call_args.kwargs["filters"].above_alt_baro == 20000


@patch("skysnoop.cli.ReAPIClient")
def test_circle_command_empty_results(mock_client_class, empty_response):
    """Test circle command with no results."""
    mock_client = AsyncMock()
    mock_client.circle.return_value = empty_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 0
    assert "No aircraft found" in result.stdout


@patch("skysnoop.cli.ReAPIClient")
def test_closest_command(mock_client_class, single_aircraft_response):
    """Test closest command."""
    mock_client = AsyncMock()
    mock_client.closest.return_value = single_aircraft_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["closest", "--", "37.7749", "-122.4194", "500"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.closest.assert_called_once()


@patch("skysnoop.cli.ReAPIClient")
def test_box_command(mock_client_class, circle_response):
    """Test box command."""
    mock_client = AsyncMock()
    mock_client.box.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["box", "--", "37.0", "38.5", "-123.0", "-121.0"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.box.assert_called_once()


@patch("skysnoop.cli.ReAPIClient")
def test_find_hex_command(mock_client_class, single_aircraft_response):
    """Test find-hex command."""
    mock_client = AsyncMock()
    mock_client.find_hex.return_value = single_aircraft_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["find-hex", "a12345"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.find_hex.assert_called_once_with("a12345")


@patch("skysnoop.cli.ReAPIClient")
def test_find_callsign_command(mock_client_class, circle_response):
    """Test find-callsign command."""
    mock_client = AsyncMock()
    mock_client.find_callsign.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["find-callsign", "UAL123"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.find_callsign.assert_called_once_with("UAL123")


@patch("skysnoop.cli.ReAPIClient")
def test_find_reg_command(mock_client_class, single_aircraft_response):
    """Test find-reg command."""
    mock_client = AsyncMock()
    mock_client.find_reg.return_value = single_aircraft_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["find-reg", "N12345"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.find_reg.assert_called_once_with("N12345")


@patch("skysnoop.cli.ReAPIClient")
def test_find_type_command(mock_client_class, circle_response):
    """Test find-type command."""
    mock_client = AsyncMock()
    mock_client.find_type.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["find-type", "A321"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.find_type.assert_called_once_with("A321")


@patch("skysnoop.cli.ReAPIClient")
def test_all_aircraft_command_with_position(mock_client_class, circle_response):
    """Test all-aircraft command (default: with position only)."""
    mock_client = AsyncMock()
    mock_client.all_with_pos.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["all-aircraft"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.all_with_pos.assert_called_once()
    mock_client.all.assert_not_called()


@patch("skysnoop.cli.ReAPIClient")
def test_all_aircraft_command_include_no_position(mock_client_class, circle_response):
    """Test all-aircraft command with --include-no-position flag."""
    mock_client = AsyncMock()
    mock_client.all.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["all-aircraft", "--include-no-position"])

    assert result.exit_code == 0
    assert "Found" in result.stdout
    mock_client.all.assert_called_once()
    mock_client.all_with_pos.assert_not_called()


@patch("skysnoop.cli.ReAPIClient")
def test_all_aircraft_command_with_filters(mock_client_class, circle_response):
    """Test all-aircraft command with filters."""
    mock_client = AsyncMock()
    mock_client.all_with_pos.return_value = circle_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["all-aircraft", "--type", "B738", "--callsign-prefix", "UAL"])

    assert result.exit_code == 0
    call_args = mock_client.all_with_pos.call_args
    assert call_args.kwargs["filters"] is not None
    assert call_args.kwargs["filters"].type_code == "B738"
    assert call_args.kwargs["filters"].callsign_prefix == "UAL"


@patch("skysnoop.cli.ReAPIClient")
def test_error_handling_api_error(mock_client_class):
    """Test error handling for API errors."""
    from skysnoop.exceptions import APIError

    mock_client = AsyncMock()
    mock_client.circle.side_effect = APIError("API request failed")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 1
    # Error messages appear in result.output (combined stdout + stderr from typer.echo)
    assert isinstance(result.exception, SystemExit)


@patch("skysnoop.cli.ReAPIClient")
def test_error_handling_timeout(mock_client_class):
    """Test error handling for timeout errors."""
    from skysnoop.exceptions import TimeoutError

    mock_client = AsyncMock()
    mock_client.circle.side_effect = TimeoutError("Request timed out")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)


@patch("skysnoop.cli.ReAPIClient")
def test_error_handling_validation_error(mock_client_class):
    """Test error handling for validation errors."""
    from skysnoop.exceptions import ValidationError

    mock_client = AsyncMock()
    mock_client.circle.side_effect = ValidationError("Invalid parameters")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client_class.return_value = mock_client

    result = runner.invoke(app, ["circle", "--", "37.7749", "-122.4194", "200"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
