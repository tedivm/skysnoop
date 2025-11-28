"""Tests for QueryFilters class."""

import pytest
from pydantic import ValidationError

from skysnoop.query.filters import QueryFilters


def test_query_filters_empty():
    """Test creating empty filters."""
    filters = QueryFilters()

    assert filters.callsign_exact is None
    assert filters.callsign_prefix is None
    assert filters.squawk is None
    assert filters.type_code is None
    assert filters.above_alt_baro is None
    assert filters.below_alt_baro is None
    assert filters.mil is None
    assert filters.pia is None
    assert filters.ladd is None


def test_query_filters_callsign_exact():
    """Test creating filters with exact callsign match."""
    filters = QueryFilters(callsign_exact="UAL123")

    assert filters.callsign_exact == "UAL123"
    assert filters.callsign_prefix is None


def test_query_filters_callsign_prefix():
    """Test creating filters with callsign prefix."""
    filters = QueryFilters(callsign_prefix="UAL")

    assert filters.callsign_prefix == "UAL"
    assert filters.callsign_exact is None


def test_query_filters_callsign_mutual_exclusion():
    """Test that callsign_exact and callsign_prefix are mutually exclusive."""
    with pytest.raises(ValidationError, match="mutually exclusive"):
        QueryFilters(callsign_exact="UAL123", callsign_prefix="UAL")


def test_query_filters_altitude_above():
    """Test creating filters with minimum altitude."""
    filters = QueryFilters(above_alt_baro=30000)

    assert filters.above_alt_baro == 30000
    assert filters.below_alt_baro is None


def test_query_filters_altitude_below():
    """Test creating filters with maximum altitude."""
    filters = QueryFilters(below_alt_baro=10000)

    assert filters.below_alt_baro == 10000
    assert filters.above_alt_baro is None


def test_query_filters_altitude_range():
    """Test creating filters with altitude range."""
    filters = QueryFilters(above_alt_baro=10000, below_alt_baro=30000)

    assert filters.above_alt_baro == 10000
    assert filters.below_alt_baro == 30000


def test_query_filters_altitude_invalid_range():
    """Test that invalid altitude range raises error."""
    with pytest.raises(ValidationError, match="must be less than"):
        QueryFilters(above_alt_baro=30000, below_alt_baro=10000)


def test_query_filters_type_code():
    """Test creating filters with aircraft type."""
    filters = QueryFilters(type_code="A321")

    assert filters.type_code == "A321"


def test_query_filters_squawk():
    """Test creating filters with squawk code."""
    filters = QueryFilters(squawk="1200")

    assert filters.squawk == "1200"


def test_query_filters_boolean_flags():
    """Test creating filters with boolean flags."""
    filters = QueryFilters(mil=True, pia=False, ladd=True)

    assert filters.mil is True
    assert filters.pia is False
    assert filters.ladd is True


def test_query_filters_to_query_params_empty():
    """Test converting empty filters to query params."""
    filters = QueryFilters()
    params = filters.to_query_params()

    assert params == {}


def test_query_filters_to_query_params_callsign_exact():
    """Test converting callsign exact filter to query params."""
    filters = QueryFilters(callsign_exact="UAL123")
    params = filters.to_query_params()

    assert params == {"filter_callsign": "UAL123"}


def test_query_filters_to_query_params_callsign_prefix():
    """Test converting callsign prefix filter to query params."""
    filters = QueryFilters(callsign_prefix="UAL")
    params = filters.to_query_params()

    assert params == {"filter_callsign_prefix": "UAL"}


def test_query_filters_to_query_params_altitude():
    """Test converting altitude filters to query params."""
    filters = QueryFilters(above_alt_baro=10000, below_alt_baro=30000)
    params = filters.to_query_params()

    assert params == {
        "filter_above_alt_baro": "10000",
        "filter_below_alt_baro": "30000",
    }


def test_query_filters_to_query_params_type():
    """Test converting type filter to query params."""
    filters = QueryFilters(type_code="A321")
    params = filters.to_query_params()

    assert params == {"filter_type": "A321"}


def test_query_filters_to_query_params_squawk():
    """Test converting squawk filter to query params."""
    filters = QueryFilters(squawk="1200")
    params = filters.to_query_params()

    assert params == {"filter_squawk": "1200"}


def test_query_filters_to_query_params_boolean_flags():
    """Test converting boolean flags to query params."""
    filters = QueryFilters(mil=True, pia=False, ladd=True)
    params = filters.to_query_params()

    assert params == {
        "filter_mil": "true",
        "filter_pia": "false",
        "filter_ladd": "true",
    }


def test_query_filters_to_query_params_multiple():
    """Test converting multiple filters to query params."""
    filters = QueryFilters(
        type_code="A321",
        above_alt_baro=20000,
        below_alt_baro=40000,
        mil=False,
    )
    params = filters.to_query_params()

    assert params == {
        "filter_type": "A321",
        "filter_above_alt_baro": "20000",
        "filter_below_alt_baro": "40000",
        "filter_mil": "false",
    }


def test_query_filters_to_query_string_empty():
    """Test converting empty filters to query string."""
    filters = QueryFilters()
    query_string = filters.to_query_string()

    assert query_string == ""


def test_query_filters_to_query_string_single():
    """Test converting single filter to query string."""
    filters = QueryFilters(type_code="A321")
    query_string = filters.to_query_string()

    assert query_string == "filter_type=A321"


def test_query_filters_to_query_string_multiple():
    """Test converting multiple filters to query string."""
    filters = QueryFilters(
        type_code="A321",
        above_alt_baro=20000,
    )
    query_string = filters.to_query_string()

    # URL encoding may reorder params, so check both are present
    assert "filter_type=A321" in query_string
    assert "filter_above_alt_baro=20000" in query_string
    assert "&" in query_string
