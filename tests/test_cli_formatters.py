"""Tests for CLI formatter functions."""

import json
from io import StringIO
from unittest.mock import patch

from skysnoop.cli_formatters import (
    format_compact,
    format_json,
    format_openapi_json,
    format_openapi_output,
    format_openapi_table,
    format_output,
    format_table,
)
from skysnoop.models.openapi import V2ResponseModel
from skysnoop.models.response import APIResponse
from skysnoop.models.skydata import SkyData


# Tests for format_json with APIResponse
def test_format_json_api_response(load_api_response):
    """Test format_json with APIResponse."""
    data = load_api_response("circle_multiple_aircraft.json")
    response = APIResponse(**data)

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_json(response)
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["resultCount"] > 0
    assert len(result["aircraft"]) > 0


def test_format_json_empty_response(load_api_response):
    """Test format_json with empty APIResponse."""
    data = load_api_response("circle_zero_results.json")
    response = APIResponse(**data)

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_json(response)
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["resultCount"] == 0
    assert len(result["aircraft"]) == 0


def test_format_json_skydata():
    """Test format_json with SkyData."""
    skydata = SkyData(
        timestamp=1234567890.0,
        result_count=1,
        backend="reapi",
        aircraft=[],
    )

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_json(skydata)
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["result_count"] == 1
    assert result["backend"] == "reapi"


# Tests for format_table with APIResponse
def test_format_table_with_aircraft(load_api_response, capsys):
    """Test format_table with aircraft data."""
    data = load_api_response("circle_multiple_aircraft.json")
    response = APIResponse(**data)

    format_table(response)
    captured = capsys.readouterr()

    assert "Found" in captured.out
    assert "aircraft" in captured.out


def test_format_table_empty_response(load_api_response, capsys):
    """Test format_table with no aircraft."""
    data = load_api_response("circle_zero_results.json")
    response = APIResponse(**data)

    format_table(response)
    captured = capsys.readouterr()

    assert "No aircraft found matching the query" in captured.out


def test_format_table_skydata(capsys):
    """Test format_table with SkyData."""
    skydata = SkyData(
        timestamp=1234567890.0,
        result_count=0,
        backend="reapi",
        aircraft=[],
    )

    format_table(skydata)
    captured = capsys.readouterr()

    assert "No aircraft found matching the query" in captured.out


# Tests for format_output
def test_format_output_json(load_api_response):
    """Test format_output with json format."""
    data = load_api_response("circle_multiple_aircraft.json")
    response = APIResponse(**data)

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_output(response, format_type="json")
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["resultCount"] > 0


def test_format_output_table(load_api_response, capsys):
    """Test format_output with table format."""
    data = load_api_response("circle_multiple_aircraft.json")
    response = APIResponse(**data)

    format_output(response, format_type="table")
    captured = capsys.readouterr()

    assert "Found" in captured.out


# Tests for format_compact
def test_format_compact_with_aircraft(load_api_response, capsys):
    """Test format_compact with aircraft data."""
    data = load_api_response("circle_multiple_aircraft.json")
    response = APIResponse(**data)

    format_compact(response)
    captured = capsys.readouterr()

    assert "Found" in captured.out
    assert "aircraft" in captured.out


def test_format_compact_empty_response(load_api_response, capsys):
    """Test format_compact with no aircraft."""
    data = load_api_response("circle_zero_results.json")
    response = APIResponse(**data)

    format_compact(response)
    captured = capsys.readouterr()

    assert "No aircraft found" in captured.out


# Tests for format_openapi_json
def test_format_openapi_json_v2_response(load_openapi_response):
    """Test format_openapi_json with V2ResponseModel."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel(**data)

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_openapi_json(response)
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["total"] >= 0
    assert "ac" in result


def test_format_openapi_json_dict():
    """Test format_openapi_json with dict response."""
    sample_dict = {
        "icao": "KSFO",
        "name": "San Francisco International Airport",
    }

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_openapi_json(sample_dict)
        output = fake_out.getvalue()

    result = json.loads(output)
    assert result["icao"] == "KSFO"


# Tests for format_openapi_table
def test_format_openapi_table_with_aircraft(load_openapi_response, capsys):
    """Test format_openapi_table with aircraft data."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel(**data)

    format_openapi_table(response)
    captured = capsys.readouterr()

    # Should show aircraft count
    assert "aircraft" in captured.out.lower() or "Found" in captured.out


def test_format_openapi_table_empty_response(load_openapi_response, capsys):
    """Test format_openapi_table with no aircraft."""
    data = load_openapi_response("v2_hex_zero_results.json")
    response = V2ResponseModel(**data)

    format_openapi_table(response)
    captured = capsys.readouterr()

    assert "No aircraft found matching the query" in captured.out


def test_format_openapi_table_dict_response(capsys):
    """Test format_openapi_table with dict response."""
    sample_dict = {
        "icao": "KSFO",
        "name": "San Francisco International Airport",
    }

    format_openapi_table(sample_dict)
    captured = capsys.readouterr()

    assert "Response:" in captured.out
    assert "KSFO" in captured.out


# Tests for format_openapi_output
def test_format_openapi_output_json(load_openapi_response):
    """Test format_openapi_output with json format."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel(**data)

    with patch("sys.stdout", new=StringIO()) as fake_out:
        format_openapi_output(response, format_type="json")
        output = fake_out.getvalue()

    result = json.loads(output)
    assert "total" in result


def test_format_openapi_output_table(load_openapi_response, capsys):
    """Test format_openapi_output with table format."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel(**data)

    format_openapi_output(response, format_type="table")
    captured = capsys.readouterr()

    assert len(captured.out) > 0  # Should have some output
