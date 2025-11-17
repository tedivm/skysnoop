# Spec Delta: API Client

## ADDED Requirements

### Requirement: HTTP Client Base

The system SHALL provide a base HTTP client class that wraps httpx.AsyncClient for communication with the adsb.lol API.

**Priority**: MUST
**Category**: API Client
**Rationale**: Foundation for all API communication; isolates HTTP concerns from domain logic.

#### Scenario: Initialize HTTP client with defaults

**Given** no configuration is provided
**When** a BaseHTTPClient is instantiated
**Then** it uses the default base URL "<https://re-api.adsb.lol/>"
**And** it uses the default timeout of 30 seconds
**And** an httpx.AsyncClient is created internally

#### Scenario: Initialize HTTP client with custom settings

**Given** a custom base URL and timeout value
**When** a BaseHTTPClient is instantiated with these settings
**Then** it uses the provided base URL
**And** it uses the provided timeout value

#### Scenario: Make GET request with query string

**Given** a BaseHTTPClient instance
**And** a pre-formatted query string (e.g., "circle=52.5,13.4,100")
**When** the get() method is called
**Then** an HTTP GET request is made to the API
**And** the URL is constructed as "{base_url}?{query_string}"
**And** commas in the query string are NOT URL-encoded
**And** the response JSON is returned as a dictionary

**NOTE**: The API requires comma-separated values (e.g., `circle=lat,lon,radius`). Using httpx's `params` parameter would URL-encode commas to `%2C`, causing 400 errors. Therefore, query strings must be pre-formatted and appended directly to the URL.

---

### Requirement: Context Manager Support

The system SHALL support async context manager protocol for proper resource cleanup.

**Priority**: MUST
**Category**: API Client
**Rationale**: Ensures HTTP connections are properly closed and resources are cleaned up.

#### Scenario: Use client as async context manager

**Given** a BaseHTTPClient instance
**When** used with async with statement
**Then** the context manager is entered successfully
**And** requests can be made within the context
**And** the httpx client is closed when exiting the context

#### Scenario: Cleanup on context exit

**Given** a BaseHTTPClient in an async context
**When** the context exits (normally or via exception)
**Then** all HTTP connections are closed
**And** resources are properly released

---

### Requirement: ADSBLol API Client

The system SHALL provide a high-level API client with methods for all adsb.lol query types.

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides developer-friendly interface for all API query capabilities.

#### Scenario: Query aircraft in circular area

**Given** an ADSBLolClient instance
**And** latitude, longitude, and radius values
**When** the circle() method is called
**Then** a request is made with circle query parameters
**And** an APIResponse object is returned
**And** the response contains aircraft within the specified area

#### Scenario: Find closest aircraft

**Given** an ADSBLolClient instance
**And** latitude, longitude, and radius values
**When** the closest() method is called
**Then** a request is made with closest query parameters
**And** an APIResponse with at most one aircraft is returned

#### Scenario: Query aircraft in bounding box

**Given** an ADSBLolClient instance
**And** latitude/longitude coordinates for opposite corners
**When** the box() method is called
**Then** a request is made with box query parameters
**And** an APIResponse with aircraft in the box is returned

---

### Requirement: Aircraft Lookup Methods

The system SHALL provide methods to lookup aircraft by identifier, callsign, registration, and type.

**Priority**: MUST
**Category**: API Client
**Rationale**: Core API functionality for finding specific aircraft.

#### Scenario: Find aircraft by ICAO hex

**Given** an ADSBLolClient instance
**And** a valid ICAO hex identifier
**When** the find_hex() method is called
**Then** a request is made with find_hex query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by callsign

**Given** an ADSBLolClient instance
**And** a flight callsign string
**When** the find_callsign() method is called
**Then** a request is made with find_callsign query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by registration

**Given** an ADSBLolClient instance
**And** an aircraft registration string
**When** the find_reg() method is called
**Then** a request is made with find_reg query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by type code

**Given** an ADSBLolClient instance
**And** an aircraft type code (e.g., "A321", "B738")
**When** the find_type() method is called
**Then** a request is made with find_type query parameter
**And** an APIResponse with matching aircraft is returned

---

### Requirement: Bulk Query Methods

The system SHALL provide methods to retrieve all aircraft with or without position requirements.

**Priority**: MUST
**Category**: API Client
**Rationale**: Supports use cases requiring visibility into all tracked aircraft.

#### Scenario: Get all aircraft with positions

**Given** an ADSBLolClient instance
**When** the all_with_pos() method is called
**Then** a request is made with all_with_pos query parameter
**And** an APIResponse with all positioned aircraft is returned

#### Scenario: Get all tracked aircraft

**Given** an ADSBLolClient instance
**When** the all() method is called
**Then** a request is made with all query parameter
**And** an APIResponse with all aircraft (with or without position) is returned

---

### Requirement: Filter Integration

The system SHALL accept optional QueryFilters parameter in all query methods.

**Priority**: MUST
**Category**: API Client
**Rationale**: Allows users to refine queries with altitude, type, callsign, and other filters.

#### Scenario: Apply filters to circle query

**Given** an ADSBLolClient instance
**And** circle query parameters
**And** a QueryFilters object with altitude and type filters
**When** the circle() method is called with the filters
**Then** the request includes both circle and filter parameters
**And** only aircraft matching all criteria are returned

#### Scenario: Query without filters

**Given** an ADSBLolClient instance
**And** query parameters with no filters
**When** any query method is called
**Then** the request includes only the query type parameters
**And** no filter parameters are added

---

### Requirement: Error Handling

The system SHALL raise appropriate exceptions for network errors, timeouts, and invalid responses.

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides clear error feedback and allows users to implement retry logic.

#### Scenario: Handle network connection error

**Given** an ADSBLolClient instance
**And** the API is unreachable
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception message indicates network failure

#### Scenario: Handle timeout error

**Given** an ADSBLolClient instance
**And** a request that exceeds the timeout duration
**When** any query method is called
**Then** a TimeoutError exception is raised
**And** the exception message indicates timeout

#### Scenario: Handle invalid JSON response

**Given** an ADSBLolClient instance
**And** the API returns malformed JSON
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception message indicates JSON parsing failure

#### Scenario: Handle HTTP error status

**Given** an ADSBLolClient instance
**And** the API returns a 4xx or 5xx status code
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception includes the status code and response text

---

### Requirement: Configurable Base URL

The system SHALL accept a configurable base URL to support testing and alternative API endpoints.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Enables testing with mock servers and supports potential API endpoint changes.

#### Scenario: Use custom API endpoint

**Given** a custom base URL
**When** an ADSBLolClient is created with this URL
**Then** all requests are sent to the custom endpoint
**And** query parameters are appended correctly

---

### Requirement: Request Timeout Configuration

The system SHALL accept a configurable timeout value for HTTP requests.

**Priority**: MUST
**Category**: API Client
**Rationale**: Allows users to adjust timeout based on network conditions and use case requirements.

#### Scenario: Use custom timeout value

**Given** a timeout value of 60 seconds
**When** an ADSBLolClient is created with this timeout
**Then** all requests use the specified timeout
**And** requests exceeding this duration raise TimeoutError

#### Scenario: Use default timeout

**Given** no timeout is specified
**When** an ADSBLolClient is created
**Then** the default timeout of 30 seconds is used

---

### Requirement: Connection Reuse

The system SHALL reuse HTTP connections across multiple requests for efficiency.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Improves performance by avoiding connection overhead for multiple queries.

#### Scenario: Multiple requests with same client

**Given** an ADSBLolClient instance in an async context
**When** multiple query methods are called sequentially
**Then** the underlying httpx client connection is reused
**And** no additional connection overhead is incurred

---

### Requirement: Type-Safe Return Values

The system SHALL return strongly-typed APIResponse objects from all query methods.

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides IDE autocomplete, type checking, and prevents runtime type errors.

#### Scenario: Return type annotations

**Given** any ADSBLolClient query method
**When** inspected with type checking tools
**Then** the return type is annotated as APIResponse
**And** mypy type checking passes

#### Scenario: Access typed response fields

**Given** an APIResponse returned from a query
**When** fields are accessed (aircraft, resultCount, etc.)
**Then** IDE provides autocomplete for field names
**And** field types match model annotations
