# aircraft-data-models Specification Delta

## ADDED Requirements

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
**And** they work with ADSBLolClient responses

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
