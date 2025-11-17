# query-filtering Specification

## Purpose
TBD - created by archiving change add-core-sdk-client. Update Purpose after archive.
## Requirements
### Requirement: Query Filters Data Structure

The system SHALL provide a QueryFilters class for defining filter criteria that can be applied to API queries.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Centralizes filter definition and enables type-safe filter construction.

#### Scenario: Create filters with altitude constraints

**Given** altitude filter values (above and/or below)
**When** a QueryFilters object is created with these values
**Then** the filters object contains the altitude constraints
**And** all values are properly typed

#### Scenario: Create filters with callsign criteria

**Given** a callsign exact match or prefix value
**When** a QueryFilters object is created with this value
**Then** the filters object contains the callsign criteria
**And** only one callsign filter type is set (exact or prefix)

#### Scenario: Create filters with type code

**Given** an aircraft type code (e.g., "A321")
**When** a QueryFilters object is created with this value
**Then** the filters object contains the type filter
**And** the value is a string

#### Scenario: Create empty filters

**Given** no filter parameters
**When** a QueryFilters object is created
**Then** all filter fields are None
**And** the object is valid

---

### Requirement: Altitude Filtering

The system SHALL support filtering aircraft by minimum and/or maximum barometric altitude.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Common use case for finding aircraft at specific altitude ranges.

#### Scenario: Filter above altitude

**Given** a QueryFilters with above_alt_baro set to 30000
**When** applied to an API query
**Then** the query includes "filter_above_alt_baro=30000"
**And** only aircraft above 30000 feet are returned

#### Scenario: Filter below altitude

**Given** a QueryFilters with below_alt_baro set to 10000
**When** applied to an API query
**Then** the query includes "filter_below_alt_baro=10000"
**And** only aircraft below 10000 feet are returned

#### Scenario: Filter altitude range

**Given** a QueryFilters with both above_alt_baro (10000) and below_alt_baro (30000)
**When** applied to an API query
**Then** the query includes both altitude filter parameters
**And** only aircraft between 10000 and 30000 feet are returned

---

### Requirement: Callsign Filtering

The system SHALL support filtering aircraft by exact callsign match or callsign prefix.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Enables finding specific flights or all flights from an airline.

#### Scenario: Filter by exact callsign

**Given** a QueryFilters with callsign_exact set to "UAL123"
**When** applied to an API query
**Then** the query includes "filter_callsign_exact=UAL123"
**And** only aircraft with callsign "UAL123" are returned

#### Scenario: Filter by callsign prefix

**Given** a QueryFilters with callsign_prefix set to "UAL"
**When** applied to an API query
**Then** the query includes "filter_callsign_prefix=UAL"
**And** only aircraft with callsigns starting with "UAL" are returned

#### Scenario: Validate mutually exclusive callsign filters

**Given** a QueryFilters with both callsign_exact and callsign_prefix set
**When** validated or applied to a query
**Then** a ValidationError is raised
**And** the error message indicates only one callsign filter type is allowed

---

### Requirement: Squawk Code Filtering

The system SHALL support filtering aircraft by squawk (transponder code).

**Priority**: SHOULD
**Category**: Query Filtering
**Rationale**: Useful for finding aircraft in emergency or special situations.

#### Scenario: Filter by squawk code

**Given** a QueryFilters with squawk set to "7700"
**When** applied to an API query
**Then** the query includes "filter_squawk=7700"
**And** only aircraft with squawk code 7700 are returned

#### Scenario: Filter standard squawk

**Given** a QueryFilters with squawk set to "1200"
**When** applied to an API query
**Then** the query includes "filter_squawk=1200"
**And** only aircraft with squawk code 1200 are returned

---

### Requirement: Aircraft Type Filtering

The system SHALL support filtering aircraft by type code.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Enables finding specific aircraft models or types.

#### Scenario: Filter by aircraft type

**Given** a QueryFilters with type_code set to "A321"
**When** applied to an API query
**Then** the query includes "filter_type=A321"
**And** only Airbus A321 aircraft are returned

#### Scenario: Filter by multiple types (if supported)

**Given** a QueryFilters with type_code set to "B738"
**When** applied to an API query
**Then** the query includes "filter_type=B738"
**And** only Boeing 737-800 aircraft are returned

---

### Requirement: Position Requirement Filter

The system SHALL support filtering to include only aircraft with position data.

**Priority**: SHOULD
**Category**: Query Filtering
**Rationale**: Useful for excluding aircraft without location information.

#### Scenario: Filter aircraft with positions

**Given** a QueryFilters with with_pos set to True
**When** applied to an API query
**Then** the query includes "filter_with_pos=true"
**And** only aircraft with latitude/longitude data are returned

---

### Requirement: Database Flag Filtering

The system SHALL support filtering by database flags (military, PIA, LADD).

**Priority**: SHOULD
**Category**: Query Filtering
**Rationale**: Enables filtering based on aircraft registration database attributes.

#### Scenario: Filter military aircraft

**Given** a QueryFilters with mil set to True
**When** applied to an API query
**Then** the query includes "filter_mil=true"
**And** only military aircraft are returned

#### Scenario: Filter PIA aircraft

**Given** a QueryFilters with pia set to True
**When** applied to an API query
**Then** the query includes "filter_pia=true"
**And** only Privacy ICAO Address (PIA) aircraft are returned

#### Scenario: Filter LADD aircraft

**Given** a QueryFilters with ladd set to True
**When** applied to an API query
**Then** the query includes "filter_ladd=true"
**And** only Limited Aircraft Data Displayed (LADD) aircraft are returned

---

### Requirement: Query Builder

The system SHALL provide a QueryBuilder class that constructs URL query strings from query objects and filters.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Centralizes URL parameter construction logic for consistency and testability. Must return strings, not dicts, to avoid httpx URL-encoding commas.

#### Scenario: Build circle query string

**Given** a QueryBuilder instance
**And** circle query parameters (lat=37.7749, lon=-122.4194, radius=200)
**When** build_circle() is called
**Then** a query string "circle=37.7749,-122.4194,200" is returned
**And** commas are NOT URL-encoded

#### Scenario: Build query string with filters

**Given** a QueryBuilder instance
**And** circle query parameters
**And** QueryFilters with altitude and type filters
**When** build_circle() is called with the filters
**Then** a query string with circle and filter parameters is returned
**And** all parameters are properly formatted (e.g., "circle=37.7749,-122.4194,200&filter_above_alt_baro=10000&filter_type=A321")
**And** commas in structural values (lat,lon,radius) are NOT encoded
**And** only filter values with special characters are URL-encoded

#### Scenario: Build find query string

**Given** a QueryBuilder instance
**And** a hex identifier "abc123"
**When** build_find_hex() is called
**Then** a query string "find_hex=abc123" is returned

---

### Requirement: Filter Validation

The system SHALL validate filter values and combinations before sending to the API.

**Priority**: SHOULD
**Category**: Query Filtering
**Rationale**: Prevents invalid API requests and provides clear error messages.

#### Scenario: Validate altitude range

**Given** a QueryFilters with above_alt_baro greater than below_alt_baro
**When** the filters are validated
**Then** a ValidationError is raised
**And** the error message indicates invalid altitude range

#### Scenario: Validate callsign format

**Given** a QueryFilters with an invalid callsign format
**When** the filters are validated
**Then** a ValidationError is raised
**And** the error message indicates invalid callsign

#### Scenario: Validate squawk format

**Given** a QueryFilters with a non-numeric squawk code
**When** the filters are validated
**Then** a ValidationError is raised
**And** the error message indicates invalid squawk format

---

### Requirement: Filter Combination

The system SHALL support combining multiple filter types in a single query.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Enables complex queries combining multiple criteria.

#### Scenario: Combine altitude and type filters

**Given** a QueryFilters with altitude range and type code
**When** applied to a circle query
**Then** the query includes all filter parameters
**And** only aircraft matching all criteria are returned

#### Scenario: Combine multiple filters

**Given** a QueryFilters with altitude, callsign prefix, and type filters
**When** applied to any query
**Then** all filter parameters are included in the request
**And** the API applies all filters

---

### Requirement: Filter Serialization

The system SHALL serialize QueryFilters to URL query parameters correctly.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Ensures filters are properly encoded for HTTP requests.

#### Scenario: Serialize boolean filters

**Given** a QueryFilters with mil=True
**When** serialized to URL parameters
**Then** the parameter is "filter_mil=true" (lowercase string)

#### Scenario: Serialize numeric filters

**Given** a QueryFilters with above_alt_baro=30000
**When** serialized to URL parameters
**Then** the parameter is "filter_above_alt_baro=30000"

#### Scenario: Serialize string filters

**Given** a QueryFilters with callsign_exact="UAL123"
**When** serialized to URL parameters
**Then** the parameter is "filter_callsign_exact=UAL123"
**And** special characters are properly URL-encoded

---

### Requirement: Empty Filter Handling

The system SHALL omit filter parameters with None values from API requests.

**Priority**: MUST
**Category**: Query Filtering
**Rationale**: Avoids sending unnecessary parameters and potential API errors.

#### Scenario: Omit None filter values

**Given** a QueryFilters with only some fields set
**When** serialized to URL parameters
**Then** only non-None fields are included
**And** None fields are omitted from the request

#### Scenario: All filters None

**Given** a QueryFilters with all fields set to None
**When** serialized to URL parameters
**Then** an empty dictionary is returned
**Or** only the base query parameters are included

