"""Tests for OpenAPI models."""

import json
from pathlib import Path

import pytest

from skysnoop.models.openapi import HTTPValidationError, V2ResponseLastPosition, V2ResponseModel, ValidationError


@pytest.fixture
def openapi_responses_dir() -> Path:
    """Return the path to the OpenAPI responses fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "openapi_responses"


@pytest.fixture
def load_openapi_response(openapi_responses_dir: Path):
    """Load an OpenAPI response fixture from a JSON file.

    Returns:
        A function that accepts a filename and returns the parsed JSON data.
    """

    def _load(filename: str) -> dict:
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


def test_v2_response_model_with_aircraft(load_openapi_response):
    """Test V2ResponseModel can parse response with aircraft."""
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    assert isinstance(response, V2ResponseModel)
    assert response.total > 0
    assert len(response.ac) > 0
    assert response.msg == "No error"
    assert response.ctime > 0
    assert response.now > 0
    assert response.ptime >= 0  # Can be 0


def test_v2_response_model_single_aircraft(load_openapi_response):
    """Test V2ResponseModel with single aircraft."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel.model_validate(data)

    assert response.total == 1
    assert len(response.ac) == 1
    aircraft = response.ac[0]
    assert aircraft.hex == "ae5a06"
    assert aircraft.messages > 0


def test_v2_response_model_zero_results(load_openapi_response):
    """Test V2ResponseModel with zero results."""
    data = load_openapi_response("v2_hex_zero_results.json")
    response = V2ResponseModel.model_validate(data)

    assert response.total == 0
    assert len(response.ac) == 0
    assert response.msg == "No error"


def test_v2_response_ac_item_required_fields(load_openapi_response):
    """Test V2ResponseAcItem has required fields."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel.model_validate(data)
    aircraft = response.ac[0]

    # Required fields
    assert isinstance(aircraft.hex, str)
    assert isinstance(aircraft.messages, int)
    assert isinstance(aircraft.seen, float)
    assert isinstance(aircraft.rssi, float)
    assert isinstance(aircraft.mlat, list)
    assert isinstance(aircraft.tisb, list)
    assert isinstance(aircraft.type, str)


def test_v2_response_ac_item_optional_fields(load_openapi_response):
    """Test V2ResponseAcItem handles optional fields correctly."""
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    # Find an aircraft with position data
    aircraft_with_pos = None
    for ac in response.ac:
        if ac.lat is not None and ac.lon is not None:
            aircraft_with_pos = ac
            break

    assert aircraft_with_pos is not None
    assert isinstance(aircraft_with_pos.lat, float)
    assert isinstance(aircraft_with_pos.lon, float)
    assert -90 <= aircraft_with_pos.lat <= 90
    assert -180 <= aircraft_with_pos.lon <= 180


def test_v2_response_ac_item_altitude_types(load_openapi_response):
    """Test V2ResponseAcItem handles different altitude types."""
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    # alt_baro can be int, str ("ground"), or None
    for aircraft in response.ac:
        if aircraft.alt_baro is not None:
            assert isinstance(aircraft.alt_baro, (int, str))
            if isinstance(aircraft.alt_baro, str):
                assert aircraft.alt_baro == "ground"


def test_v2_response_last_position(load_openapi_response):
    """Test V2ResponseLastPosition model."""
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    # Find an aircraft with last_position
    aircraft_with_last_pos = None
    for ac in response.ac:
        if ac.last_position is not None:
            aircraft_with_last_pos = ac
            break

    if aircraft_with_last_pos and aircraft_with_last_pos.last_position:
        last_pos = aircraft_with_last_pos.last_position
        assert isinstance(last_pos, V2ResponseLastPosition)
        assert isinstance(last_pos.lat, float)
        assert isinstance(last_pos.lon, float)
        assert isinstance(last_pos.nic, int)
        assert isinstance(last_pos.rc, int)
        assert isinstance(last_pos.seen_pos, float)


def test_v2_response_ac_item_serialization(load_openapi_response):
    """Test V2ResponseAcItem can be serialized back to dict."""
    data = load_openapi_response("v2_hex_single.json")
    response = V2ResponseModel.model_validate(data)
    aircraft = response.ac[0]

    # Serialize back to dict
    aircraft_dict = aircraft.model_dump(mode="json", exclude_none=True)
    assert isinstance(aircraft_dict, dict)
    assert aircraft_dict["hex"] == "ae5a06"


def test_v2_response_model_serialization(load_openapi_response):
    """Test V2ResponseModel can be serialized to JSON."""
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    # Serialize to dict
    response_dict = response.model_dump(mode="json", exclude_none=True)
    assert isinstance(response_dict, dict)
    assert "ac" in response_dict
    assert "total" in response_dict
    assert "msg" in response_dict

    # Can be converted to JSON
    json_str = json.dumps(response_dict)
    assert isinstance(json_str, str)


def test_validation_error_model():
    """Test ValidationError model."""
    error = ValidationError(
        loc=["body", "param1"],
        msg="Field required",
        type="value_error.missing",
    )

    assert error.loc == ["body", "param1"]
    assert error.msg == "Field required"
    assert error.type == "value_error.missing"


def test_http_validation_error_model():
    """Test HTTPValidationError model."""
    error_detail = ValidationError(
        loc=["body", "lat"],
        msg="ensure this value is greater than or equal to -90",
        type="value_error.number.not_ge",
    )

    http_error = HTTPValidationError(detail=[error_detail])

    assert len(http_error.detail) == 1
    assert http_error.detail[0].loc == ["body", "lat"]


def test_http_validation_error_model_empty():
    """Test HTTPValidationError with no details."""
    http_error = HTTPValidationError()
    assert http_error.detail is None


def test_v2_response_ac_item_alias_fields(load_openapi_response):
    """Test V2ResponseAcItem handles aliased fields correctly."""
    # Some fields use aliases like dbFlags -> db_flags
    data = load_openapi_response("v2_mil_response.json")
    response = V2ResponseModel.model_validate(data)

    # Find aircraft with dbFlags
    for aircraft in response.ac:
        if aircraft.db_flags is not None:
            assert isinstance(aircraft.db_flags, int)
            break


def test_v2_response_model_forward_compatibility(load_openapi_response):
    """Test V2ResponseModel handles extra fields (forward compatibility)."""
    data = load_openapi_response("v2_hex_single.json")

    # Add extra field not in model
    data["extra_field"] = "should_be_ignored"
    data["ac"][0]["new_field"] = 123

    # Should still parse without error (Pydantic ignores extra fields by default)
    response = V2ResponseModel.model_validate(data)
    assert response.total == 1
