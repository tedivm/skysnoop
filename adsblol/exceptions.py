"""Custom exceptions for the adsblol library.

This module defines the exception hierarchy used throughout the library
for clear and specific error handling.
"""


class ADSBLolError(Exception):
    """Base exception for all adsblol errors.

    All custom exceptions in the adsblol library inherit from this base class,
    allowing users to catch all library-specific errors with a single except clause.
    """

    pass


class APIError(ADSBLolError):
    """Raised when the adsb.lol API returns an error response.

    This includes HTTP errors (4xx, 5xx status codes) and malformed responses
    from the API server.

    Examples:
        - 404 Not Found when a resource doesn't exist
        - 500 Internal Server Error from the API
        - Invalid JSON response from the server
    """

    pass


class ValidationError(ADSBLolError):
    """Raised when input validation fails before making an API request.

    This exception is raised when client-side validation detects invalid
    parameters (e.g., latitude out of range, negative radius) before
    attempting to contact the API.

    Examples:
        - Latitude value outside [-90, 90]
        - Longitude value outside [-180, 180]
        - Negative radius for circle queries
        - Invalid hex code format
    """

    pass


class TimeoutError(ADSBLolError):
    """Raised when an API request exceeds the configured timeout period.

    This exception indicates that the API server did not respond within
    the specified timeout duration. This could be due to network issues,
    server overload, or an unreachable endpoint.

    Examples:
        - API request takes longer than configured timeout (default 30s)
        - Network connectivity issues
        - Server under heavy load
    """

    pass
