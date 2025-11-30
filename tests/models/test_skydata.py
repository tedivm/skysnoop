"""Tests for SkyData unified response model."""

import pytest

from skysnoop.models import Aircraft, SkyData


def test_skydata_initialization():
    """Test SkyData model initialization with required fields."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=2,
        processing_time=15.5,
        aircraft=[
            Aircraft(hex="abc123", flight="TEST123"),
            Aircraft(hex="def456", flight="TEST456"),
        ],
        backend="reapi",
        simulated=False,
    )

    assert data.timestamp == 1234567890.5
    assert data.result_count == 2
    assert data.processing_time == 15.5
    assert len(data.aircraft) == 2
    assert data.backend == "reapi"
    assert data.simulated is False


def test_skydata_optional_processing_time():
    """Test SkyData with None processing_time (OpenAPI backend)."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=1,
        processing_time=None,
        aircraft=[Aircraft(hex="abc123")],
        backend="openapi",
    )

    assert data.processing_time is None
    assert data.backend == "openapi"


def test_skydata_default_simulated():
    """Test SkyData simulated field defaults to False."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=0,
        aircraft=[],
        backend="openapi",
    )

    assert data.simulated is False


def test_skydata_simulated_true():
    """Test SkyData with simulated=True (simulated operation)."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=1,
        aircraft=[Aircraft(hex="abc123")],
        backend="openapi",
        simulated=True,
    )

    assert data.simulated is True


def test_skydata_count_property():
    """Test count property returns result_count."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=5,
        aircraft=[Aircraft(hex=f"ac{i}") for i in range(5)],
        backend="reapi",
    )

    assert data.count == 5
    assert data.count == data.result_count


def test_skydata_has_results_property():
    """Test has_results property."""
    # With results
    data_with_results = SkyData(
        timestamp=1234567890.5,
        result_count=1,
        aircraft=[Aircraft(hex="abc123")],
        backend="reapi",
    )
    assert data_with_results.has_results is True

    # Without results
    data_no_results = SkyData(
        timestamp=1234567890.5,
        result_count=0,
        aircraft=[],
        backend="reapi",
    )
    assert data_no_results.has_results is False


def test_skydata_len():
    """Test __len__ returns aircraft list length."""
    aircraft_list = [Aircraft(hex=f"ac{i}") for i in range(3)]
    data = SkyData(
        timestamp=1234567890.5,
        result_count=3,
        aircraft=aircraft_list,
        backend="reapi",
    )

    assert len(data) == 3
    assert len(data) == len(aircraft_list)


def test_skydata_iter():
    """Test __iter__ iterates over aircraft list."""
    aircraft_list = [
        Aircraft(hex="abc123", flight="TEST1"),
        Aircraft(hex="def456", flight="TEST2"),
        Aircraft(hex="ghi789", flight="TEST3"),
    ]
    data = SkyData(
        timestamp=1234567890.5,
        result_count=3,
        aircraft=aircraft_list,
        backend="reapi",
    )

    iterated_aircraft = list(data)
    assert iterated_aircraft == aircraft_list

    # Test iteration in for loop
    hex_codes = []
    for aircraft in data:
        hex_codes.append(aircraft.hex)
    assert hex_codes == ["abc123", "def456", "ghi789"]


def test_skydata_str_reapi():
    """Test __str__ returns human-readable representation for RE-API."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=5,
        processing_time=12.5,
        aircraft=[Aircraft(hex=f"ac{i}") for i in range(5)],
        backend="reapi",
        simulated=False,
    )

    result = str(data)
    assert "SkyData from reapi backend with 5 aircraft" in result
    assert "processed in 12.5ms" in result
    assert "(simulated)" not in result


def test_skydata_str_openapi():
    """Test __str__ returns human-readable representation for OpenAPI."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=3,
        processing_time=None,
        aircraft=[Aircraft(hex=f"ac{i}") for i in range(3)],
        backend="openapi",
        simulated=False,
    )

    result = str(data)
    assert "SkyData from openapi backend with 3 aircraft" in result
    assert "processed in" not in result
    assert "(simulated)" not in result


def test_skydata_str_simulated():
    """Test __str__ includes (simulated) note for simulated operations."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=2,
        aircraft=[Aircraft(hex="ac1"), Aircraft(hex="ac2")],
        backend="openapi",
        simulated=True,
    )

    result = str(data)
    assert "(simulated)" in result
    assert "SkyData from openapi backend with 2 aircraft" in result


def test_skydata_empty_aircraft_list():
    """Test SkyData with empty aircraft list."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=0,
        aircraft=[],
        backend="reapi",
    )

    assert data.count == 0
    assert data.has_results is False
    assert len(data) == 0
    assert list(data) == []


def test_skydata_backend_validation():
    """Test SkyData only accepts valid backend values."""
    # Valid backends
    for backend in ["openapi", "reapi"]:
        data = SkyData(
            timestamp=1234567890.5,
            result_count=0,
            aircraft=[],
            backend=backend,
        )
        assert data.backend == backend

    # Invalid backend should fail validation
    with pytest.raises(ValueError):
        SkyData(
            timestamp=1234567890.5,
            result_count=0,
            aircraft=[],
            backend="invalid",
        )


def test_skydata_extra_fields_allowed():
    """Test SkyData allows extra fields for forward compatibility."""
    data = SkyData(
        timestamp=1234567890.5,
        result_count=1,
        aircraft=[Aircraft(hex="abc123")],
        backend="reapi",
        extra_field="some_value",
        another_field=123,
    )

    # Extra fields should be stored
    assert data.result_count == 1
    assert data.backend == "reapi"
