# unified-client Specification

## Purpose
TBD - created by archiving change add-unified-client-abstraction. Update Purpose after archive.
## Requirements
### Requirement: Backend Protocol Interface

The system SHALL define a protocol interface that all backend adapters must implement.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Establishes the contract for backend implementations, enabling type-safe polymorphism and interchangeable backends.

#### Scenario: Protocol defines common query methods

**Given** the BackendProtocol is defined
**When** a backend adapter is created
**Then** it must implement get_by_hex(), get_by_callsign(), get_by_registration(), get_by_type()
**And** it must implement get_in_circle() and get_closest()
**And** all methods must return SkyData objects
**And** all methods must be async

#### Scenario: Protocol defines context manager support

**Given** the BackendProtocol is defined
**When** a backend adapter is created
**Then** it must implement **aenter**() and **aexit**() methods
**And** it must support async with statement for resource management

---

### Requirement: SkyData Response Model

The system SHALL provide a SkyData response model that normalizes differences between backend response types.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Provides consistent data structure regardless of backend, allowing user code to work with both APIs without changes.

#### Scenario: Normalize timestamp field

**Given** a response from either backend
**When** converted to SkyData
**Then** the timestamp field contains the server timestamp
**And** it is normalized from 'now' field in both APIResponse and V2ResponseModel

#### Scenario: Normalize result count field

**Given** a response from either backend
**When** converted to SkyData
**Then** the result_count field contains the number of aircraft
**And** it is normalized from 'resultCount' (RE-API) or 'total' (OpenAPI)

#### Scenario: Normalize aircraft list

**Given** a response from either backend
**When** converted to SkyData
**Then** the aircraft field contains a list of Aircraft objects
**And** all aircraft conform to the common Aircraft model
**And** V2ResponseAcItem objects are converted to Aircraft objects

#### Scenario: Include backend identifier

**Given** a SkyData response
**When** inspected by user code
**Then** the backend field indicates which backend provided the response
**And** the value is either "openapi" or "reapi"

#### Scenario: Provide convenience properties

**Given** a SkyData object
**When** user code accesses response properties
**Then** count property returns result_count
**And** has_results property returns True if result_count > 0
**And** len() returns the length of aircraft list
**And** iteration yields aircraft objects

---

### Requirement: OpenAPI Backend Adapter

The system SHALL provide an adapter that wraps OpenAPIClient to implement the BackendProtocol.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Enables OpenAPI to be used as a backend for the unified client interface.

#### Scenario: Initialize OpenAPI adapter

**Given** optional API key, base URL, and timeout parameters
**When** OpenAPIAdapter is instantiated
**Then** it creates an OpenAPIClient with the provided configuration
**And** it uses default base URL "<https://api.adsb.lol>" if not provided

#### Scenario: Implement get_by_hex via OpenAPI

**Given** an OpenAPIAdapter instance
**And** a hex code string
**When** get_by_hex() is called
**Then** it delegates to client.v2.get_by_hex()
**And** converts V2ResponseModel to SkyData
**And** returns SkyData with backend="openapi"

#### Scenario: Implement get_in_circle via OpenAPI

**Given** an OpenAPIAdapter instance
**And** latitude, longitude, and radius parameters
**When** get_in_circle() is called
**Then** it delegates to client.v2.get_by_point()
**And** converts V2ResponseModel to SkyData
**And** returns SkyData with backend="openapi"

#### Scenario: Convert V2ResponseModel to SkyData

**Given** a V2ResponseModel from OpenAPI
**When** the adapter converts it to SkyData
**Then** timestamp is mapped from 'now' field
**And** result_count is mapped from 'total' field
**And** processing_time is mapped from 'ctime' or 'ptime' if available
**And** aircraft list is converted from V2ResponseAcItem to Aircraft models
**And** backend is set to "openapi"

#### Scenario: Simulate box queries for OpenAPI

**Given** an OpenAPIAdapter instance
**And** box boundaries (lat_south, lat_north, lon_west, lon_east)
**When** get_in_box() is called
**Then** it calculates the center point and bounding radius
**And** queries OpenAPI with get_by_point() using calculated center and radius
**And** filters results client-side to only include aircraft within box bounds
**And** returns SkyData with filtered aircraft
**And** response metadata indicates operation was simulated

---

### Requirement: RE-API Backend Adapter

The system SHALL provide an adapter that wraps ReAPIClient to implement the BackendProtocol.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Enables RE-API to be used as a backend for the unified client interface.

#### Scenario: Initialize RE-API adapter

**Given** optional base URL and timeout parameters
**When** ReAPIAdapter is instantiated
**Then** it creates a ReAPIClient with the provided configuration
**And** it uses default base URL "<https://re-api.adsb.lol/>" if not provided

#### Scenario: Implement get_by_hex via RE-API

**Given** a ReAPIAdapter instance
**And** a hex code string
**When** get_by_hex() is called
**Then** it delegates to client.find_hex()
**And** converts APIResponse to SkyData
**And** returns SkyData with backend="reapi"

#### Scenario: Implement get_in_circle via RE-API

**Given** a ReAPIAdapter instance
**And** latitude, longitude, radius, and optional filters
**When** get_in_circle() is called
**Then** it delegates to client.circle()
**And** passes filters through unchanged
**And** converts APIResponse to SkyData
**And** returns SkyData with backend="reapi"

#### Scenario: Convert APIResponse to SkyData

**Given** an APIResponse from RE-API
**When** the adapter converts it to SkyData
**Then** timestamp is mapped from 'now' field
**And** result_count is mapped from 'resultCount' field
**And** processing_time is mapped from 'ptime' field
**And** aircraft list is passed through unchanged (already Aircraft models)
**And** backend is set to "reapi"

#### Scenario: Support native RE-API box queries

**Given** a ReAPIAdapter instance
**When** get_in_box() is called
**Then** it delegates to client.box()
**And** returns SkyData with results
**And** response indicates native backend support (not simulated)

---

### Requirement: SkySnoop Primary Interface

The system SHALL provide a high-level SkySnoop client as the primary user-facing interface that delegates to backend adapters.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Provides the main entry point for the library, abstracting backend selection and providing a consistent interface.

#### Scenario: Initialize with automatic backend selection

**Given** no backend parameter is provided
**When** SkySnoop is instantiated with backend="auto"
**Then** it attempts to select the most appropriate backend automatically
**And** it checks for API key to prefer OpenAPI
**And** it falls back to RE-API if OpenAPI is unavailable

#### Scenario: Initialize with explicit OpenAPI backend

**Given** backend="openapi" parameter
**When** SkySnoop is instantiated
**Then** it creates and uses OpenAPIAdapter
**And** all operations are delegated to OpenAPI

#### Scenario: Initialize with explicit RE-API backend

**Given** backend="reapi" parameter
**When** SkySnoop is instantiated
**Then** it creates and uses ReAPIAdapter
**And** all operations are delegated to RE-API

#### Scenario: Delegate get_by_hex to backend

**Given** a SkySnoop instance with selected backend
**And** a hex code string
**When** get_by_hex() is called
**Then** the call is delegated to the backend adapter's get_by_hex()
**And** returns SkyData from the backend

#### Scenario: Delegate get_in_circle to backend

**Given** a SkySnoop instance with selected backend
**And** latitude, longitude, and radius parameters
**When** get_in_circle() is called
**Then** the call is delegated to the backend adapter's get_in_circle()
**And** returns SkyData from the backend

#### Scenario: Support async context manager

**Given** a SkySnoop instance
**When** used with async with statement
**Then** it enters the context successfully
**And** the underlying backend adapter context is entered
**And** operations can be performed within the context
**And** resources are cleaned up on context exit

---

### Requirement: Backend Selection Strategy

The system SHALL implement intelligent automatic backend selection based on configuration and availability, preferring RE-API with OpenAPI fallback.

**Priority**: SHOULD
**Category**: Unified Client
**Rationale**: Enables seamless switching between backends without user intervention when backend="auto". Prefers RE-API since OpenAPI spec is not yet finalized. API key accepted for future compatibility but not currently required.

#### Scenario: Use OpenAPI when API key is provided

**Given** backend="auto" is specified
**And** an API key is provided or ADSBLOL_API_KEY env var is set
**When** SkySnoop is instantiated
**Then** OpenAPIAdapter is selected as the backend
**And** the API key is passed to the adapter for future compatibility
**And** note that API key is not currently required by OpenAPI

#### Scenario: Prefer RE-API when no API key and accessible

**Given** backend="auto" is specified
**And** no API key is provided
**And** RE-API is accessible
**When** SkySnoop is instantiated
**Then** ReAPIAdapter is selected as the backend
**And** operations use the stable RE-API

#### Scenario: Fallback to OpenAPI when RE-API unavailable

**Given** backend="auto" is specified
**And** no API key is provided
**And** RE-API is not accessible
**When** SkySnoop is instantiated
**Then** OpenAPIAdapter is selected as the backend
**And** operations use OpenAPI as fallback

#### Scenario: Use OpenAPI when explicitly specified

**Given** backend="openapi" is explicitly specified
**When** SkySnoop is instantiated
**Then** the client uses OpenAPIAdapter
**And** raises appropriate errors if OpenAPI is unavailable
**And** does not fall back to RE-API

#### Scenario: Use RE-API when explicitly specified

**Given** backend="reapi" is explicitly specified
**When** SkySnoop is instantiated
**Then** the client uses ReAPIAdapter
**And** raises appropriate errors if RE-API is unavailable
**And** does not fall back to OpenAPI

---

### Requirement: Method Name Normalization

The system SHALL provide normalized method names that map to equivalent operations in both backends.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Provides consistent naming convention that is backend-agnostic and intuitive.

#### Scenario: Map hex lookup methods

**Given** SkySnoop method get_by_hex()
**When** called with OpenAPI backend
**Then** it maps to v2.get_by_hex()
**When** called with RE-API backend
**Then** it maps to find_hex()

#### Scenario: Map callsign lookup methods

**Given** SkySnoop method get_by_callsign()
**When** called with OpenAPI backend
**Then** it maps to v2.get_by_callsign()
**When** called with RE-API backend
**Then** it maps to find_callsign()

#### Scenario: Map registration lookup methods

**Given** SkySnoop method get_by_registration()
**When** called with OpenAPI backend
**Then** it maps to v2.get_by_registration()
**When** called with RE-API backend
**Then** it maps to find_reg()

#### Scenario: Map circle query methods

**Given** SkySnoop method get_in_circle()
**When** called with OpenAPI backend
**Then** it maps to v2.get_by_point()
**When** called with RE-API backend
**Then** it maps to circle()

---

### Requirement: Operation Simulation for Missing Features

The system SHALL simulate operations that are not natively supported by a backend when feasible.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Provides consistent interface across backends even when features aren't natively supported, improving user experience.

#### Scenario: Simulate box queries with OpenAPI backend

**Given** SkySnoop with backend="openapi"
**And** box boundary parameters
**When** get_in_box() is called
**Then** the operation is simulated using a bounding circle query
**And** results are filtered client-side to box bounds
**And** SkyData is returned with filtered aircraft
**And** response metadata indicates simulation was used

#### Scenario: Raise error for unsupported operations

**Given** SkySnoop with backend="openapi"
**When** get_all_with_pos() is called
**Then** a NotImplementedError is raised
**And** error message indicates this operation requires RE-API backend
**And** error message mentions 250 NM radius limitation

#### Scenario: Use native operations when available

**Given** SkySnoop with backend="reapi"
**When** get_in_box() or get_all_with_pos() is called
**Then** the operation delegates to native RE-API methods
**And** no simulation or error handling is required
**And** response metadata indicates native backend support

#### Scenario: Handle military filter with RE-API backend

**Given** SkySnoop with backend="reapi"
**When** get_military() is called
**Then** it simulates the operation using all_with_pos() with filter_mil=True
**And** returns SkyData with filtered results

---

### Requirement: Filter Support Across Backends

The system SHALL support QueryFilters parameter where applicable, adapting filter behavior to backend capabilities.

**Priority**: SHOULD
**Category**: Unified Client
**Rationale**: Maintains existing filter functionality while adapting to backend-specific filter mechanisms.

#### Scenario: Pass filters to RE-API backend

**Given** a SkySnoop with RE-API backend
**And** a QueryFilters object with altitude and type filters
**When** get_in_circle() is called with the filters
**Then** the filters are passed through to client.circle() unchanged
**And** results are filtered by the backend

#### Scenario: Handle filters with OpenAPI backend

**Given** a SkySnoop with OpenAPI backend
**And** a QueryFilters object
**When** get_in_circle() is called with filters
**Then** filters are ignored (OpenAPI endpoints have built-in filtering)
**And** a warning is logged indicating filters are not supported with OpenAPI backend
**And** results are returned without filter application

---

### Requirement: Type Safety and Protocol Compliance

The system SHALL maintain strong typing with Protocol-based type checking for backend adapters.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Ensures compile-time verification that adapters implement required interface correctly. Enables shared test suite that validates all adapters consistently.#### Scenario: Type check adapter compliance

**Given** OpenAPIAdapter and ReAPIAdapter implementations
**When** type checked with mypy
**Then** both adapters conform to BackendProtocol
**And** no type errors are reported
**And** all required methods are implemented with correct signatures

#### Scenario: Shared test suite validates all adapters

**Given** a shared protocol test suite
**And** multiple adapter implementations (OpenAPIAdapter, ReAPIAdapter)
**When** the shared test suite runs
**Then** all adapters pass identical protocol compliance tests
**And** tests verify method signatures, return types, and behavior
**And** no test code is duplicated between adapter test files
**And** adding new adapters requires no new protocol tests#### Scenario: Type check SkyData

**Given** SkyData model
**When** type checked with mypy
**Then** all fields have correct type annotations
**And** convenience properties have correct return types
**And** the model validates with Pydantic

---

### Requirement: Error Exception Mapping

The system SHALL map backend-specific exceptions to common exception types where possible.

**Priority**: SHOULD
**Category**: Unified Client
**Rationale**: Provides consistent error handling across backends, reducing backend-specific error handling code.

#### Scenario: Map timeout errors

**Given** either backend adapter
**When** a timeout error occurs in the underlying client
**Then** it is raised as TimeoutError
**And** the error message indicates the timeout occurred

#### Scenario: Map API errors

**Given** either backend adapter
**When** an API error occurs in the underlying client
**Then** it is raised as APIError
**And** the error message includes backend-specific details

#### Scenario: Map validation errors

**Given** OpenAPIAdapter
**When** an OpenAPIValidationError occurs
**Then** it is raised as ValidationError
**And** validation details are preserved in the error

---

### Requirement: Context Manager Resource Cleanup

The system SHALL properly clean up resources when exiting async context managers.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Prevents resource leaks and ensures HTTP connections are properly closed.

#### Scenario: Cleanup on normal exit

**Given** a SkySnoop instance in an async context
**When** the context exits normally
**Then** the backend adapter's **aexit**() is called
**And** underlying HTTP client connections are closed
**And** resources are released

#### Scenario: Cleanup on exception

**Given** a SkySnoop instance in an async context
**And** an exception occurs during operations
**When** the context exits with the exception
**Then** the backend adapter's **aexit**() is still called
**And** underlying HTTP client connections are closed
**And** the exception is propagated

---

### Requirement: Simulated Operation Metadata

The system SHALL indicate in response metadata when an operation was simulated vs natively supported.

**Priority**: SHOULD
**Category**: Unified Client
**Rationale**: Allows users to understand how data was retrieved and make informed decisions about backend choice.

#### Scenario: Include simulation indicator in SkyData

**Given** a SkyData response from a simulated operation
**When** user inspects the response
**Then** a simulated field or metadata indicates the operation was simulated
**And** documentation explains implications of simulated operations

#### Scenario: Indicate native operation support

**Given** a SkyData response from a native operation
**When** user inspects the response
**Then** metadata indicates native backend support was used
**And** no simulation was required

---

### Requirement: Backward Compatibility

The system SHALL maintain complete backward compatibility with existing ReAPIClient and OpenAPIClient usage.

**Priority**: MUST
**Category**: Unified Client
**Rationale**: Ensures zero breaking changes for existing users while providing new unified interface option.

#### Scenario: Existing ReAPIClient code unchanged

**Given** existing code using ReAPIClient directly
**When** the unified client is added to the library
**Then** the existing code continues to work without modifications
**And** no changes to ReAPIClient public API occur

#### Scenario: Existing OpenAPIClient code unchanged

**Given** existing code using OpenAPIClient directly
**When** the unified client is added to the library
**Then** the existing code continues to work without modifications
**And** no changes to OpenAPIClient public API occur

#### Scenario: Import paths preserved

**Given** existing imports of ReAPIClient and OpenAPIClient
**When** SkySnoop is added
**Then** existing import paths continue to work
**And** SkySnoop is available as primary import: from skysnoop import SkySnoop
**And** Also available at skysnoop.client.SkySnoop for consistency

---

