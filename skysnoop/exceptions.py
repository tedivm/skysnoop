"""Custom exceptions for the skysnoop library.

This module defines the exception hierarchy used throughout the library
for clear and specific error handling.
"""


class SkySnoopError(Exception):
    """Base exception for all skysnoop errors.

    All custom exceptions in the skysnoop library inherit from this base class,
    allowing users to catch all library-specific errors with a single except clause.
    """

    pass


class APIError(SkySnoopError):
    """Raised when the adsb.lol API returns an error response.

    This includes HTTP errors (4xx, 5xx status codes) and malformed responses
    from the API server.

    Examples:
        - 404 Not Found when a resource doesn't exist
        - 500 Internal Server Error from the API
        - Invalid JSON response from the server
    """

    pass


class ValidationError(SkySnoopError):
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


class TimeoutError(SkySnoopError):
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


class OpenAPIValidationError(SkySnoopError):
    """Raised when the OpenAPI endpoint returns a 422 validation error.

    This exception indicates that the request parameters failed server-side
    validation. The exception includes detailed field-level error information
    from the API response.

    Attributes:
        details: List of validation error details from the API
        status_code: HTTP status code (422)

    Examples:
        - Invalid parameter format
        - Missing required parameters
        - Parameter value out of acceptable range
    """

    def __init__(self, message: str, details: list | None = None, status_code: int = 422):
        """Initialize OpenAPIValidationError.

        Args:
            message: Error message
            details: Optional list of validation error details
            status_code: HTTP status code
        """
        super().__init__(message)
        self.details = details or []
        self.status_code = status_code


class AuthenticationError(SkySnoopError):
    """Raised when the OpenAPI endpoint returns a 401 authentication error.

    This exception indicates that the API key is missing, invalid, or expired.
    Users need to provide a valid API key to access protected endpoints.

    Examples:
        - No API key provided for protected endpoint
        - Invalid or malformed API key
        - Expired API key
    """

    pass


class RateLimitError(SkySnoopError):
    """Raised when the OpenAPI endpoint returns a 429 rate limit error.

    This exception indicates that the client has exceeded the rate limit for
    API requests. The retry_after attribute indicates how long to wait before
    making another request.

    Attributes:
        retry_after: Optional number of seconds to wait before retrying

    Examples:
        - Too many requests in a short time period
        - Exceeded daily/hourly API quota
    """

    def __init__(self, message: str, retry_after: int | None = None):
        """Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Optional seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after
