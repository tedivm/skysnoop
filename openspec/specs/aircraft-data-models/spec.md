# aircraft-data-models Specification

## Purpose
TBD - created by archiving change add-core-sdk-client. Update Purpose after archive.
## Requirements
### Requirement: Aircraft Data Model

The system SHALL provide a Pydantic model representing aircraft telemetry data with all fields from the adsb.lol API response.

**Priority**: MUST  
**Category**: Data Model  
**Rationale**: Core data structure for all aircraft operations; must support all API fields for complete functionality.

#### Scenario: Parse complete aircraft object

**Given** a JSON response from the adsb.lol API containing a full aircraft object with all fields  
**When** the JSON is parsed into an Aircraft model  
**Then** all fields are correctly mapped to their typed attributes  
**And** numeric values are properly converted  
**And** timestamp fields are handled correctly  
**And** optional fields default to None when missing

#### Scenario: Handle partial aircraft data

**Given** a JSON response with only required aircraft fields (hex, type)  
**When** the JSON is parsed into an Aircraft model  
**Then** the model is created successfully  
**And** optional fields are set to None  
**And** no validation errors are raised

#### Scenario: Validate aircraft position data

**Given** an Aircraft model with latitude and longitude values  
**When** the position is accessed  
**Then** latitude is between -90 and 90 degrees  
**And** longitude is between -180 and 180 degrees  
**And** altitude values are numeric or None

---

### Requirement: API Response Model

The system SHALL provide a Pydantic model for API responses containing metadata and aircraft list.

**Priority**: MUST  
**Category**: Data Model  
**Rationale**: Wraps aircraft data with server metadata (timestamp, count, processing time) for complete API response representation.

#### Scenario: Parse API response with multiple aircraft

**Given** a JSON response with resultCount, now, ptime, and aircraft array  
**When** the JSON is parsed into an APIResponse model  
**Then** the resultCount matches the aircraft list length  
**And** the now timestamp is a float  
**And** the ptime (processing time) is a float  
**And** all aircraft are parsed into Aircraft models

#### Scenario: Parse API response with zero aircraft

**Given** a JSON response with resultCount of 0 and empty aircraft array  
**When** the JSON is parsed into an APIResponse model  
**Then** the model is created successfully  
**And** the aircraft list is empty  
**And** metadata fields are present

---

### Requirement: Optional Field Handling

The system SHALL make all aircraft telemetry fields optional except the ICAO hex identifier.

**Priority**: MUST  
**Category**: Data Model  
**Rationale**: API does not guarantee all fields in every response; models must handle missing data gracefully.

#### Scenario: Create aircraft with only hex identifier

**Given** JSON data containing only the hex field  
**When** parsed into an Aircraft model  
**Then** the model is created successfully  
**And** the hex field is populated  
**And** all other fields are None

#### Scenario: Access missing optional field

**Given** an Aircraft model with a missing altitude field  
**When** the altitude field is accessed  
**Then** the value is None  
**And** no exception is raised

---

### Requirement: Type Conversions

The system SHALL perform automatic type conversions for numeric strings and timestamps in aircraft data.

**Priority**: SHOULD  
**Category**: Data Model  
**Rationale**: API may return some numeric values as strings; automatic conversion improves usability.

#### Scenario: Convert string coordinates to floats

**Given** aircraft JSON with latitude/longitude as strings  
**When** parsed into an Aircraft model  
**Then** the coordinates are converted to float values  
**And** the values are numerically correct

#### Scenario: Convert timestamp to float

**Given** aircraft JSON with a seen timestamp as a string  
**When** parsed into an Aircraft model  
**Then** the timestamp is converted to a float  
**And** the value represents epoch time

---

### Requirement: Computed Properties

The system SHALL provide computed properties on the Aircraft model for common derived values.

**Priority**: SHOULD  
**Category**: Data Model  
**Rationale**: Convenience properties improve developer experience for common queries without manual field checking.

#### Scenario: Check if aircraft has position

**Given** an Aircraft model with lat and lon values  
**When** the has_position property is accessed  
**Then** it returns True

#### Scenario: Check aircraft without position

**Given** an Aircraft model with no lat or lon values  
**When** the has_position property is accessed  
**Then** it returns False

#### Scenario: Get age of position data

**Given** an Aircraft model with a seen_pos timestamp  
**And** the current time is known  
**When** the position_age property is accessed  
**Then** it returns the time difference in seconds

---

### Requirement: Forward Compatibility

The system SHALL use Pydantic's `extra="allow"` configuration to accept unknown fields in API responses.

**Priority**: MUST  
**Category**: Data Model  
**Rationale**: API may add new fields in the future; models should not break when encountering unknown fields.

#### Scenario: Parse response with unknown field

**Given** aircraft JSON containing a new field not in the model  
**When** parsed into an Aircraft model  
**Then** the model is created successfully  
**And** known fields are populated correctly  
**And** the unknown field is preserved in the model's extra data

---

### Requirement: Field Aliases

The system SHALL support field aliases for API fields that conflict with Python keywords or conventions.

**Priority**: SHOULD  
**Category**: Data Model  
**Rationale**: Some API fields may conflict with Python keywords (e.g., 'type'); aliases allow proper mapping.

#### Scenario: Map reserved keyword field

**Given** aircraft JSON with a field name that is a Python keyword  
**When** parsed into an Aircraft model  
**Then** the field is mapped to an aliased attribute name  
**And** the value is accessible via the alias

---

### Requirement: Model Serialization

The system SHALL support serialization of Aircraft and APIResponse models back to JSON and dictionary formats.

**Priority**: MUST  
**Category**: Data Model  
**Rationale**: Users need to serialize models for logging, storage, or API responses.

#### Scenario: Serialize aircraft to JSON

**Given** an Aircraft model with populated fields  
**When** the model is serialized to JSON  
**Then** the output is valid JSON  
**And** all non-None fields are included  
**And** field names match the original API format

#### Scenario: Serialize aircraft to dictionary

**Given** an Aircraft model with populated fields  
**When** the model is converted to a dictionary  
**Then** the output is a Python dict  
**And** all non-None fields are included  
**And** nested objects are properly serialized

### Requirement: OpenAPI V2 Response Models

The system SHALL provide Pydantic models for OpenAPI v2 response schemas.

**Priority**: MUST
**Category**: Data Models
**Rationale**: Enables type-safe parsing of OpenAPI v2 responses and provides IDE autocomplete.

#### Scenario: Parse V2 API response

**Given** a JSON response from an OpenAPI v2 endpoint
**When** the response is parsed into a V2Response_Model
**Then** the model validates successfully
**And** the model has fields: ac, ctime, msg, now, ptime, total
**And** the ac field is a list of V2Response_AcItem objects

#### Scenario: Parse V2 aircraft item

**Given** an aircraft object from a v2 response
**When** parsed into V2Response_AcItem
**Then** required fields are present: hex, messages, mlat, rssi, seen, tisb, type
**And** optional fields are properly typed with None union
**And** position fields (lat, lon) are nullable
**And** altitude fields (alt_baro, alt_geom) support int, string, or None

#### Scenario: Handle lastPosition nested object

**Given** a V2 aircraft item with lastPosition field
**When** parsed into V2Response_AcItem
**Then** lastPosition is typed as V2Response_LastPosition or None
**And** if present, it contains lat, lon, nic, rc, seen_pos fields
**And** all fields have correct types

#### Scenario: Generate models from OpenAPI schema

**Given** the OpenAPI v2 schemas in the spec
**When** datamodel-code-generator runs
**Then** V2Response_Model class is generated
**And** V2Response_AcItem class is generated
**And** V2Response_LastPosition class is generated
**And** all classes inherit from pydantic.BaseModel
**And** all fields have correct types matching the OpenAPI schema

---

### Requirement: OpenAPI V0 Response Models

The system SHALL provide models for OpenAPI v0 endpoint responses.

**Priority**: SHOULD
**Category**: Data Models
**Rationale**: Enables type-safe access to v0 airport and route data.

#### Scenario: Parse airport response

**Given** a JSON response from /api/0/airport/{icao}
**When** parsed with v0 models
**Then** the response is a string or structured airport data
**And** the model validates successfully

#### Scenario: Parse route set response

**Given** a JSON response from /api/0/routeset
**When** parsed with v0 models
**Then** route information for requested aircraft is returned
**And** the model validates successfully

#### Scenario: Parse receiver information

**Given** a JSON response from /0/me
**When** parsed with v0 models
**Then** receiver information and global stats are returned
**And** the model validates successfully

---

### Requirement: Model Organization for Multiple APIs

The system SHALL organize models by API type to prevent naming conflicts.

**Priority**: MUST
**Category**: Data Models
**Rationale**: Allows re-api and OpenAPI models to coexist with clear namespacing.

#### Scenario: Import re-api models

**Given** a user wants to use re-api models
**When** importing from adsblol.models
**Then** Aircraft and APIResponse are available
**And** they work with ReAPIClient responses

#### Scenario: Import OpenAPI v2 models

**Given** a user wants to use OpenAPI v2 models
**When** importing from adsblol.models.openapi.v2
**Then** V2Response_Model and related classes are available
**And** they work with OpenAPIClient v2 responses

#### Scenario: Import OpenAPI v0 models

**Given** a user wants to use OpenAPI v0 models
**When** importing from adsblol.models.openapi.v0
**Then** v0 model classes are available
**And** they work with OpenAPIClient v0 responses

#### Scenario: No model name conflicts

**Given** both re-api and OpenAPI models loaded
**When** using models in code
**Then** there are no naming conflicts
**And** each model is in its own namespace
**And** types are clearly distinguishable

---

### Requirement: OpenAPI Model Field Mapping

The system SHALL map OpenAPI schema field names to Pydantic model attributes.

**Priority**: MUST
**Category**: Data Models
**Rationale**: Ensures generated models match API response structure exactly.

#### Scenario: Map camelCase fields

**Given** OpenAPI schemas with fields like "lastPosition"
**When** models are generated
**Then** field names match the schema exactly (lastPosition, not last_position)
**And** Pydantic serialization preserves field names

#### Scenario: Map snake_case fields

**Given** OpenAPI schemas with fields like "alt_baro"
**When** models are generated
**Then** field names use snake_case as specified
**And** no case conversion is applied

#### Scenario: Handle optional fields

**Given** OpenAPI schema fields marked as not required
**When** models are generated
**Then** fields are typed with | None union
**And** fields can be omitted in responses
**And** accessing missing fields returns None

---

### Requirement: Backward Compatibility with Re-API Models

The system SHALL maintain backward compatibility with existing re-api models.

**Priority**: MUST
**Category**: Data Models
**Rationale**: Ensures existing code using re-api models continues to work.

#### Scenario: Existing Aircraft model unchanged

**Given** the existing Aircraft model in adsblol.models.aircraft
**When** OpenAPI models are added
**Then** the Aircraft model is unchanged
**And** existing code using Aircraft continues to work
**And** no breaking changes are introduced

#### Scenario: Existing APIResponse model unchanged

**Given** the existing APIResponse model in adsblol.models.response
**When** OpenAPI models are added
**Then** the APIResponse model is unchanged
**And** existing code using APIResponse continues to work
**And** iteration and access patterns remain the same

---

### Requirement: Model Documentation

The system SHALL generate docstrings for OpenAPI models from the spec.

**Priority**: SHOULD
**Category**: Data Models
**Rationale**: Improves developer experience with inline documentation.

#### Scenario: Models have class docstrings

**Given** OpenAPI schemas with description fields
**When** models are generated
**Then** each model class has a docstring
**And** the docstring includes the schema description
**And** the docstring is visible in IDE tooltips

#### Scenario: Fields have descriptions

**Given** OpenAPI schema fields with descriptions
**When** models are generated
**Then** each field has a description in Field() definition
**And** descriptions are visible in IDE parameter hints

