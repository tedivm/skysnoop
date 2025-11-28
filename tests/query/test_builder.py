"""Tests for QueryBuilder class."""

from skysnoop.query.builder import QueryBuilder
from skysnoop.query.filters import QueryFilters


def test_build_circle_basic():
    """Test building basic circle query."""
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200)

    assert query == "circle=37.7749,-122.4194,200"
    assert "," in query  # Verify commas are preserved
    assert "%2C" not in query  # Verify commas are NOT encoded


def test_build_circle_with_filters():
    """Test building circle query with filters."""
    filters = QueryFilters(type_code="A321", above_alt_baro=20000)
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

    assert query.startswith("circle=37.7749,-122.4194,200&")
    assert "filter_type=A321" in query
    assert "filter_above_alt_baro=20000" in query


def test_build_circle_with_empty_filters():
    """Test building circle query with empty filters."""
    filters = QueryFilters()
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

    # Empty filters should not add anything to the query
    assert query == "circle=37.7749,-122.4194,200"


def test_build_closest_basic():
    """Test building basic closest query."""
    query = QueryBuilder.build_closest(lat=37.7749, lon=-122.4194, radius=200)

    assert query == "closest=37.7749,-122.4194,200"
    assert "," in query


def test_build_closest_with_filters():
    """Test building closest query with filters."""
    filters = QueryFilters(mil=True)
    query = QueryBuilder.build_closest(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

    assert query.startswith("closest=37.7749,-122.4194,200&")
    assert "filter_mil=true" in query


def test_build_box_basic():
    """Test building basic box query."""
    query = QueryBuilder.build_box(
        lat_south=37.0,
        lat_north=38.5,
        lon_west=-123.0,
        lon_east=-121.0,
    )

    assert query == "box=37.0,38.5,-123.0,-121.0"
    assert "," in query


def test_build_box_with_filters():
    """Test building box query with filters."""
    filters = QueryFilters(callsign_prefix="UAL")
    query = QueryBuilder.build_box(
        lat_south=37.0,
        lat_north=38.5,
        lon_west=-123.0,
        lon_east=-121.0,
        filters=filters,
    )

    assert query.startswith("box=37.0,38.5,-123.0,-121.0&")
    assert "filter_callsign_prefix=UAL" in query


def test_build_find_hex():
    """Test building find_hex query."""
    query = QueryBuilder.build_find_hex("abc123")

    assert query == "find_hex=abc123"


def test_build_find_callsign():
    """Test building find_callsign query."""
    query = QueryBuilder.build_find_callsign("UAL123")

    assert query == "find_callsign=UAL123"


def test_build_find_reg():
    """Test building find_reg query."""
    query = QueryBuilder.build_find_reg("N12345")

    assert query == "find_reg=N12345"


def test_build_find_type():
    """Test building find_type query."""
    query = QueryBuilder.build_find_type("A321")

    assert query == "find_type=A321"


def test_build_all_basic():
    """Test building basic all query."""
    query = QueryBuilder.build_all()

    assert query == "all"


def test_build_all_with_filters():
    """Test building all query with filters."""
    filters = QueryFilters(below_alt_baro=10000)
    query = QueryBuilder.build_all(filters=filters)

    assert query.startswith("all&")
    assert "filter_below_alt_baro=10000" in query


def test_build_all_with_pos_basic():
    """Test building basic all_with_pos query."""
    query = QueryBuilder.build_all_with_pos()

    assert query == "all_with_pos"


def test_build_all_with_pos_with_filters():
    """Test building all_with_pos query with filters."""
    filters = QueryFilters(type_code="B738")
    query = QueryBuilder.build_all_with_pos(filters=filters)

    assert query.startswith("all_with_pos&")
    assert "filter_type=B738" in query


def test_build_circle_negative_coordinates():
    """Test building circle query with negative coordinates."""
    query = QueryBuilder.build_circle(lat=-33.8688, lon=151.2093, radius=100)

    assert query == "circle=-33.8688,151.2093,100"


def test_build_multiple_filters():
    """Test building query with multiple filters."""
    filters = QueryFilters(
        type_code="A321",
        above_alt_baro=20000,
        below_alt_baro=40000,
        mil=False,
    )
    query = QueryBuilder.build_circle(lat=37.7749, lon=-122.4194, radius=200, filters=filters)

    assert query.startswith("circle=37.7749,-122.4194,200&")
    assert "filter_type=A321" in query
    assert "filter_above_alt_baro=20000" in query
    assert "filter_below_alt_baro=40000" in query
    assert "filter_mil=false" in query


def test_comma_preservation():
    """Test that commas are preserved in all query types."""
    queries = [
        QueryBuilder.build_circle(lat=1.1, lon=2.2, radius=100),
        QueryBuilder.build_closest(lat=1.1, lon=2.2, radius=100),
        QueryBuilder.build_box(lat_south=1.1, lat_north=2.2, lon_west=3.3, lon_east=4.4),
    ]

    for query in queries:
        assert "," in query
        assert "%2C" not in query
        assert "%2c" not in query
