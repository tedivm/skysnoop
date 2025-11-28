# api-client Specification

## Purpose

TBD - created by archiving change add-core-sdk-client. Update Purpose after archive.

## Requirements

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

**Given** an ReAPIClient instance
**And** latitude, longitude, and radius values
**When** the circle() method is called
**Then** a request is made with circle query parameters
**And** an APIResponse object is returned
**And** the response contains aircraft within the specified area

#### Scenario: Find closest aircraft

**Given** an ReAPIClient instance
**And** latitude, longitude, and radius values
**When** the closest() method is called
**Then** a request is made with closest query parameters
**And** an APIResponse with at most one aircraft is returned

#### Scenario: Query aircraft in bounding box

**Given** an ReAPIClient instance
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

**Given** an ReAPIClient instance
**And** a valid ICAO hex identifier
**When** the find_hex() method is called
**Then** a request is made with find_hex query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by callsign

**Given** an ReAPIClient instance
**And** a flight callsign string
**When** the find_callsign() method is called
**Then** a request is made with find_callsign query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by registration

**Given** an ReAPIClient instance
**And** an aircraft registration string
**When** the find_reg() method is called
**Then** a request is made with find_reg query parameter
**And** an APIResponse with matching aircraft is returned

#### Scenario: Find aircraft by type code

**Given** an ReAPIClient instance
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

**Given** an ReAPIClient instance
**When** the all_with_pos() method is called
**Then** a request is made with all_with_pos query parameter
**And** an APIResponse with all positioned aircraft is returned

#### Scenario: Get all tracked aircraft

**Given** an ReAPIClient instance
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

**Given** an ReAPIClient instance
**And** circle query parameters
**And** a QueryFilters object with altitude and type filters
**When** the circle() method is called with the filters
**Then** the request includes both circle and filter parameters
**And** only aircraft matching all criteria are returned

#### Scenario: Query without filters

**Given** an ReAPIClient instance
**And** query parameters with no filters
**When** any query method is called
**Then** the request includes only the query type parameters
**And** no filter parameters are added

---

### Requirement: Error Handling

The system SHALL raise appropriate exceptions for network errors, timeouts, and invalid responses.

**Changes**: Extended to include OpenAPI-specific errors (ValidationError, AuthenticationError, RateLimitError).

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides clear error feedback and allows users to implement retry logic for both APIs.

#### Scenario: Handle network connection error

**Given** an ReAPIClient or OpenAPIClient instance
**And** the API is unreachable
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception message indicates network failure

#### Scenario: Handle timeout error

**Given** an ReAPIClient or OpenAPIClient instance
**And** a request that exceeds the timeout duration
**When** any query method is called
**Then** a TimeoutError exception is raised
**And** the exception message indicates timeout

#### Scenario: Handle invalid JSON response

**Given** an ReAPIClient or OpenAPIClient instance
**And** the API returns malformed JSON
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception message indicates JSON parsing failure

#### Scenario: Handle HTTP error status

**Given** an ReAPIClient or OpenAPIClient instance
**And** the API returns a 4xx or 5xx status code
**When** any query method is called
**Then** an APIError exception is raised
**And** the exception includes the status code and response text

### Requirement: Configurable Base URL

The system SHALL accept a configurable base URL to support testing and alternative API endpoints.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Enables testing with mock servers and supports potential API endpoint changes.

#### Scenario: Use custom API endpoint

**Given** a custom base URL
**When** an ReAPIClient is created with this URL
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
**When** an ReAPIClient is created with this timeout
**Then** all requests use the specified timeout
**And** requests exceeding this duration raise TimeoutError

#### Scenario: Use default timeout

**Given** no timeout is specified
**When** an ReAPIClient is created
**Then** the default timeout of 30 seconds is used

---

### Requirement: Connection Reuse

The system SHALL reuse HTTP connections across multiple requests for efficiency.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Improves performance by avoiding connection overhead for multiple queries.

#### Scenario: Multiple requests with same client

**Given** an ReAPIClient instance in an async context
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

**Given** any ReAPIClient query method
**When** inspected with type checking tools
**Then** the return type is annotated as APIResponse
**And** mypy type checking passes

#### Scenario: Access typed response fields

**Given** an APIResponse returned from a query
**When** fields are accessed (aircraft, resultCount, etc.)
**Then** IDE provides autocomplete for field names
**And** field types match model annotations

### Requirement: OpenAPI Client Base

The system SHALL provide an OpenAPI client class for communication with the adsb.lol OpenAPI endpoints.

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides access to the new adsb.lol OpenAPI that works globally without feeder IP restrictions.

#### Scenario: Initialize OpenAPI client with defaults

**Given** no configuration is provided
**When** an OpenAPIClient is instantiated
**Then** it uses the default base URL "<https://api.adsb.lol>"
**And** it uses the default timeout of 30 seconds
**And** an httpx.AsyncClient is created internally
**And** no API key is set (keys not required yet)

#### Scenario: Initialize OpenAPI client with API key

**Given** an API key string
**When** an OpenAPIClient is instantiated with the API key
**Then** it uses the provided API key for requests
**And** the key is included in request headers

#### Scenario: Initialize OpenAPI client from environment

**Given** the SKYSNOOP_API_KEY environment variable is set
**When** an OpenAPIClient is instantiated without an explicit API key
**Then** it uses the API key from the environment variable

---

### Requirement: OpenAPI V2 Endpoint Methods

The system SHALL provide methods for all adsb.lol OpenAPI v2 endpoints.

**Priority**: MUST
**Category**: API Client
**Rationale**: Core functionality for querying aircraft data via the new API.

#### Scenario: Query aircraft with PIA addresses

**Given** an OpenAPIClient instance
**When** the v2.get_pia() method is called
**Then** a GET request is made to /v2/pia
**And** a V2Response object with PIA aircraft is returned

#### Scenario: Query military aircraft

**Given** an OpenAPIClient instance
**When** the v2.get_mil() method is called
**Then** a GET request is made to /v2/mil
**And** a V2Response object with military aircraft is returned

#### Scenario: Query aircraft on LADD

**Given** an OpenAPIClient instance
**When** the v2.get_ladd() method is called
**Then** a GET request is made to /v2/ladd
**And** a V2Response object with LADD-filtered aircraft is returned

#### Scenario: Query by squawk code

**Given** an OpenAPIClient instance
**And** a squawk code string (e.g., "7700")
**When** the v2.get_by_squawk(squawk) method is called
**Then** a GET request is made to /v2/squawk/{squawk}
**And** a V2Response object with matching aircraft is returned

#### Scenario: Query by aircraft type

**Given** an OpenAPIClient instance
**And** an aircraft type code (e.g., "A320")
**When** the v2.get_by_type(aircraft_type) method is called
**Then** a GET request is made to /v2/type/{aircraft_type}
**And** a V2Response object with matching aircraft is returned

#### Scenario: Query by registration

**Given** an OpenAPIClient instance
**And** a registration string (e.g., "G-KELS")
**When** the v2.get_by_registration(registration) method is called
**Then** a GET request is made to /v2/registration/{registration}
**And** a V2Response object with matching aircraft is returned

#### Scenario: Query by ICAO hex

**Given** an OpenAPIClient instance
**And** an ICAO hex code (e.g., "4CA87C")
**When** the v2.get_by_hex(icao_hex) method is called
**Then** a GET request is made to /v2/hex/{icao_hex}
**And** a V2Response object with matching aircraft is returned

#### Scenario: Query by callsign

**Given** an OpenAPIClient instance
**And** a callsign string (e.g., "JBU1942")
**When** the v2.get_by_callsign(callsign) method is called
**Then** a GET request is made to /v2/callsign/{callsign}
**And** a V2Response object with matching aircraft is returned

#### Scenario: Query by point and radius

**Given** an OpenAPIClient instance
**And** latitude, longitude, and radius values
**When** the v2.get_by_point(lat, lon, radius) method is called
**Then** a GET request is made to /v2/point/{lat}/{lon}/{radius}
**And** a V2Response object with aircraft in the circle is returned

#### Scenario: Find closest aircraft

**Given** an OpenAPIClient instance
**And** latitude, longitude, and radius values
**When** the v2.get_closest(lat, lon, radius) method is called
**Then** a GET request is made to /v2/closest/{lat}/{lon}/{radius}
**And** a V2Response object with the closest aircraft is returned

---

### Requirement: OpenAPI V0 Endpoint Methods

The system SHALL provide methods for adsb.lol OpenAPI v0 endpoints.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Provides access to auxiliary data like airport information and routes.

#### Scenario: Query airport by ICAO code

**Given** an OpenAPIClient instance
**And** an airport ICAO code (e.g., "KJFK")
**When** the v0.get_airport(icao) method is called
**Then** a GET request is made to /api/0/airport/{icao}
**And** airport data is returned as a dictionary

#### Scenario: Query routes for multiple aircraft

**Given** an OpenAPIClient instance
**And** a list of aircraft with callsigns and positions
**When** the v0.get_routes(planes) method is called
**Then** a POST request is made to /api/0/routeset
**And** route data for the aircraft is returned

#### Scenario: Get receiver information

**Given** an OpenAPIClient instance
**When** the v0.get_me() method is called
**Then** a GET request is made to /0/me
**And** receiver and global stats are returned

---

### Requirement: OpenAPI Model Generation

The system SHALL generate Pydantic models from the OpenAPI specification.

**Priority**: MUST
**Category**: API Client
**Rationale**: Ensures type safety and keeps models synchronized with API schema changes.

#### Scenario: Models generated from spec

**Given** the OpenAPI specification at <https://api.adsb.lol/api/openapi.json>
**When** the openapi-generate make target is run
**Then** Pydantic v2 models are generated in skysnoop/models/openapi/
**And** models include V2Response_Model, V2Response_AcItem, and related schemas
**And** all models have proper type hints matching the spec

#### Scenario: Models validate API responses

**Given** generated OpenAPI models
**And** a response from the adsb.lol OpenAPI
**When** the response is parsed into a model
**Then** Pydantic validation succeeds
**And** all fields are accessible with correct types
**And** optional fields are properly marked

---

### Requirement: OpenAPI Spec Monitoring

The system SHALL monitor the OpenAPI specification for changes.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Ensures the client stays synchronized with API updates.

#### Scenario: Weekly spec check

**Given** a GitHub Actions workflow
**When** the workflow runs on schedule (weekly)
**Then** the latest OpenAPI spec is fetched
**And** the spec hash is compared with the stored version
**And** if changed, a GitHub issue is created notifying maintainers

#### Scenario: Manual spec update

**Given** the openapi-update make target
**When** a developer runs make openapi-update
**Then** the latest spec is downloaded
**And** models are regenerated using datamodel-code-generator
**And** the spec version and hash are updated in openapi_version.py
**And** the developer is prompted to review changes

---

### Requirement: OpenAPI Update Assistance

The system SHALL provide a GitHub Copilot prompt for assisted OpenAPI client updates.

**Priority**: SHOULD
**Category**: API Client
**Rationale**: Guides developers through non-mechanical aspects of API updates.

#### Scenario: Update client with Copilot prompt

**Given** the GitHub Copilot prompt at .github/prompts/update-openapi-client.prompt.md
**And** the OpenAPI spec has changed
**When** a developer invokes Copilot with the prompt
**Then** Copilot reviews the spec changes
**And** Copilot identifies breaking changes
**And** Copilot updates client methods to match new/changed endpoints
**And** Copilot updates or creates tests for changed functionality
**And** Copilot updates documentation to reflect API changes

#### Scenario: Prompt guides spec download

**Given** the update-openapi-client prompt
**When** invoked by a developer
**Then** the prompt instructs to download the latest spec
**And** the prompt instructs to compare versions
**And** the prompt provides steps for regenerating models
**And** the prompt checks for breaking changes in schemas

---

### Requirement: OpenAPI Version Tracking

The system SHALL track the OpenAPI specification version and update timestamp.

**Priority**: MUST
**Category**: API Client
**Rationale**: Enables runtime version checks and debugging.

#### Scenario: Store spec metadata

**Given** an OpenAPI spec with version "0.0.2"
**When** models are generated
**Then** the version is stored in openapi_version.py
**And** the spec hash is stored
**And** the generation timestamp is stored

#### Scenario: Log version at client initialization

**Given** an OpenAPIClient instance
**When** the client is instantiated
**Then** the OpenAPI spec version is logged at DEBUG level
**And** the spec hash is available for debugging

---

### Requirement: OpenAPI Error Handling

The system SHALL handle OpenAPI-specific errors appropriately.

**Priority**: MUST
**Category**: API Client
**Rationale**: Provides clear error feedback for API-specific error conditions.

#### Scenario: Handle 422 validation error

**Given** an OpenAPIClient instance
**And** an invalid parameter value
**When** a query method is called
**Then** a ValidationError is raised
**And** the error includes field-level validation details from the API
**And** the error message clearly indicates the invalid field

#### Scenario: Handle unauthorized error

**Given** an OpenAPIClient instance
**And** an invalid or missing API key
**When** a query method is called (once keys are required)
**Then** an AuthenticationError is raised
**And** the error message indicates authentication failure
**And** the error message provides guidance on obtaining an API key

#### Scenario: Handle rate limit error

**Given** an OpenAPIClient instance
**And** the API rate limit has been exceeded
**When** a query method is called
**Then** a RateLimitError is raised
**And** the error includes retry-after information if available
**And** the error message suggests reducing request frequency

---

