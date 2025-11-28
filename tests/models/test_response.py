"""Tests for APIResponse model."""

from skysnoop.models import Aircraft, APIResponse


def test_api_response_with_aircraft(load_api_response):
    """Test APIResponse model with aircraft data from real API response."""
    data = load_api_response("circle_multiple_aircraft.json")

    response = APIResponse(**data)

    assert response.now > 0
    assert response.resultCount > 0
    assert response.ptime >= 0
    assert len(response.aircraft) == response.resultCount
    assert all(isinstance(ac, Aircraft) for ac in response.aircraft)


def test_api_response_zero_results(load_api_response):
    """Test APIResponse model with zero aircraft."""
    data = load_api_response("circle_zero_results.json")

    response = APIResponse(**data)

    assert response.now > 0
    assert response.resultCount == 0
    assert response.ptime >= 0
    assert len(response.aircraft) == 0
    assert not response.has_results


def test_api_response_single_aircraft(load_api_response):
    """Test APIResponse model with single aircraft."""
    data = load_api_response("closest_response.json")

    response = APIResponse(**data)

    assert response.resultCount == 1
    assert len(response.aircraft) == 1
    assert response.has_results
    assert isinstance(response.aircraft[0], Aircraft)


def test_api_response_count_property(load_api_response):
    """Test that count property returns resultCount."""
    data = load_api_response("circle_multiple_aircraft.json")

    response = APIResponse(**data)

    assert response.count == response.resultCount


def test_api_response_has_results_true(load_api_response):
    """Test has_results property when aircraft are present."""
    data = load_api_response("circle_single_aircraft.json")

    response = APIResponse(**data)

    assert response.has_results is True


def test_api_response_has_results_false(load_api_response):
    """Test has_results property when no aircraft are present."""
    data = load_api_response("circle_zero_results.json")

    response = APIResponse(**data)

    assert response.has_results is False


def test_api_response_len(load_api_response):
    """Test __len__ method returns number of aircraft."""
    data = load_api_response("circle_multiple_aircraft.json")

    response = APIResponse(**data)

    assert len(response) == len(response.aircraft)
    assert len(response) == response.resultCount


def test_api_response_iter(load_api_response):
    """Test that APIResponse is iterable over aircraft."""
    data = load_api_response("circle_single_aircraft.json")

    response = APIResponse(**data)

    aircraft_list = list(response)
    assert len(aircraft_list) == response.resultCount
    assert all(isinstance(ac, Aircraft) for ac in aircraft_list)


def test_api_response_str_representation(load_api_response):
    """Test string representation of APIResponse."""
    data = load_api_response("circle_multiple_aircraft.json")

    response = APIResponse(**data)

    str_repr = str(response)
    assert "APIResponse" in str_repr
    assert str(response.resultCount) in str_repr
    assert str(response.ptime) in str_repr


def test_api_response_serialization(load_api_response):
    """Test APIResponse serialization to dict."""
    data = load_api_response("closest_response.json")

    response = APIResponse(**data)

    response_dict = response.model_dump()
    assert "now" in response_dict
    assert "resultCount" in response_dict
    assert "ptime" in response_dict
    assert "aircraft" in response_dict
    assert len(response_dict["aircraft"]) == response.resultCount


def test_api_response_forward_compatibility(load_api_response):
    """Test that APIResponse handles unknown fields gracefully."""
    data = load_api_response("circle_zero_results.json")
    data["unknown_field"] = "test_value"
    data["future_metric"] = 99.9

    # Should not raise an error due to extra="allow"
    response = APIResponse(**data)
    assert response.resultCount == 0


def test_api_response_empty_aircraft_list():
    """Test APIResponse with manually created empty aircraft list."""
    response = APIResponse(now=1234567890.0, resultCount=0, ptime=5.0, aircraft=[])

    assert response.resultCount == 0
    assert len(response.aircraft) == 0
    assert not response.has_results


def test_api_response_with_manual_aircraft():
    """Test APIResponse with manually created aircraft."""
    aircraft = Aircraft(hex="test123", lat=37.5, lon=-122.4)

    response = APIResponse(now=1234567890.0, resultCount=1, ptime=10.0, aircraft=[aircraft])

    assert response.resultCount == 1
    assert len(response.aircraft) == 1
    assert response.aircraft[0].hex == "test123"
    assert response.has_results
