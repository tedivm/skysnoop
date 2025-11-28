"""Tests for the exceptions module."""

import pytest

from skysnoop.exceptions import APIError, SkySnoopError, TimeoutError, ValidationError


def test_exception_hierarchy():
    """Test that all exceptions inherit from SkySnoopError."""
    assert issubclass(APIError, SkySnoopError)
    assert issubclass(ValidationError, SkySnoopError)
    assert issubclass(TimeoutError, SkySnoopError)


def test_skysnoop_error():
    """Test SkySnoopError can be raised and caught."""
    with pytest.raises(SkySnoopError) as exc_info:
        raise SkySnoopError("test error")
    assert str(exc_info.value) == "test error"


def test_api_error():
    """Test APIError can be raised and caught."""
    with pytest.raises(APIError) as exc_info:
        raise APIError("API request failed")
    assert str(exc_info.value) == "API request failed"

    # Should also be catchable as SkySnoopError
    with pytest.raises(SkySnoopError):
        raise APIError("test")


def test_validation_error():
    """Test ValidationError can be raised and caught."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Invalid input")
    assert str(exc_info.value) == "Invalid input"

    # Should also be catchable as SkySnoopError
    with pytest.raises(SkySnoopError):
        raise ValidationError("test")


def test_timeout_error():
    """Test TimeoutError can be raised and caught."""
    with pytest.raises(TimeoutError) as exc_info:
        raise TimeoutError("Request timed out")
    assert str(exc_info.value) == "Request timed out"

    # Should also be catchable as SkySnoopError
    with pytest.raises(SkySnoopError):
        raise TimeoutError("test")
