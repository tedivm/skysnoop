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

