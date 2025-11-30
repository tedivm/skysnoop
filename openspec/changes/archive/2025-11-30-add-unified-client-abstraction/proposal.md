# Proposal: Add Unified Client Abstraction

## Summary

Create a unified client abstraction layer (SkySnoop) that provides a consistent interface across both the OpenAPI and RE-API clients. This enables users to write backend-agnostic code that works with either API without modification, allowing seamless switching based on deployment context, access restrictions, or feature requirements.

## Motivation

Currently, `skysnoop` provides two distinct client implementations with different interfaces, methods, and capabilities:

- **OpenAPIClient**: Modern public API with structured v2/v0 endpoints, uses `v2.get_by_hex()` style methods, returns `V2ResponseModel`
- **ReAPIClient**: Legacy feeder-only API with IP-based access, uses `find_hex()` style methods, returns `APIResponse`

Users must write different code depending on which API they're using. Switching between APIs requires code changes throughout their application. This creates several problems:

1. **Code Duplication**: Users need separate implementations for each backend
2. **Tight Coupling**: Application logic is tightly coupled to specific API client
3. **Migration Difficulty**: Moving from one API to another requires extensive refactoring
4. **Testing Complexity**: Testing with different backends requires conditional logic
5. **Limited Flexibility**: Cannot easily switch backends based on runtime conditions

## Goals

1. **Primary User Interface**: Provide SkySnoop as the main entry point for the library with a single, consistent API
2. **Transparent Backend Selection**: Allow runtime or configuration-based backend selection with automatic fallback
3. **Type Safety**: Maintain strong typing with unified response models
4. **Feature Parity Mapping**: Map equivalent operations between APIs with clear documentation
5. **Graceful Degradation**: Handle operations not available in selected backend with helpful error messages
6. **Zero Breaking Changes**: Existing client code continues to work unchanged
7. **Easy Migration**: Provide simple path for users to adopt unified interface incrementally

## Non-Goals

- Merging the two underlying clients into a single implementation
- Removing or deprecating existing client APIs
- Implementing missing features in either backend API
- Creating a new third API endpoint
- Providing 100% feature parity between backends (some operations are backend-specific)

## Scope

### In Scope

- **Core Components**:
  - `BackendProtocol`: Protocol defining the interface contract for all backend adapters
  - `SkyData`: Response data model normalizing differences between backend response types
  - `OpenAPIAdapter`: Adapter wrapping OpenAPIClient to implement BackendProtocol
  - `ReAPIAdapter`: Adapter wrapping ReAPIClient to implement BackendProtocol
  - `SkySnoop`: High-level client providing the unified interface (primary user-facing API)

- **Common Operations**:
  - Aircraft lookup by hex, callsign, registration, type
  - Spatial queries: circle/point, closest
  - Filter support where applicable
  - Context manager support for resource cleanup

- **Backend Selection**:
  - Uses OpenAPI when API key is provided (accepted for future compatibility, not currently required)
  - Prefers stable RE-API backend when no API key and accessible (OpenAPI spec not yet finalized)
  - Falls back to OpenAPI when RE-API is not accessible
  - Explicit backend selection (`backend="openapi"` or `backend="reapi"`)
  - Environment variable support (`ADSBLOL_API_KEY`)

- **Error Handling**:
  - Unsupported operation errors with helpful messages
  - Exception mapping from backend-specific to common exceptions
  - Clear indication of which backend provides which features

- **Documentation**:
  - Comprehensive docstrings with usage examples
  - README updates with unified client documentation
  - Method mapping documentation (unified → OpenAPI/RE-API)
  - Feature availability matrix

- **CLI Integration**:
  - Add `--backend` flag to CLI commands
  - Support backend selection in CLI
  - Maintain backward compatibility with existing CLI behavior
  - Update CLI help text and documentation

### Out of Scope

- Caching layer
- Automatic failover between backends
- Load balancing across multiple backend instances
- Metrics and monitoring
- V0 endpoint support (get_routes, get_airport, etc.) - accessed via direct client
- Advanced features unique to one backend (e.g., detailed RE-API box queries with complex filters)

## Design Approach

The implementation uses the **Adapter Pattern** combined with **Strategy Pattern**:

- **Protocol**: `BackendProtocol` defines the interface contract using Python's `typing.Protocol`
- **Adapters**: `OpenAPIAdapter` and `ReAPIAdapter` wrap existing clients to conform to the protocol
- **Strategy**: `SkySnoop` delegates to the selected adapter based on `backend` parameter
- **Normalization**: `SkyData` provides a common response model across backends

See `design.md` for detailed architecture, component specifications, and design decisions.

## Method Mapping

| Unified Method | OpenAPI Method | RE-API Method | Notes |
|----------------|----------------|---------------|-------|
| `get_by_hex()` | `v2.get_by_hex()` | `find_hex()` | Direct equivalent |
| `get_by_callsign()` | `v2.get_by_callsign()` | `find_callsign()` | Direct equivalent |
| `get_by_registration()` | `v2.get_by_registration()` | `find_reg()` | Direct equivalent |
| `get_by_type()` | `v2.get_by_type()` | `find_type()` | Direct equivalent |
| `get_in_circle()` | `v2.get_by_point()` | `circle()` | Direct equivalent |
| `get_closest()` | `v2.get_closest()` | `closest()` | Direct equivalent |
| `get_in_box()` | Simulated* | `box()` | OpenAPI simulated via circle + filter, RE-API native |
| `get_all_with_pos()` | Not Available | `all_with_pos()` | RE-API only (OpenAPI has 250 NM max radius) |
| `get_military()` | `v2.get_mil()` | Simulated via filters | OpenAPI native, RE-API simulated |
| `get_pia()` | `v2.get_pia()` | Simulated via filters | OpenAPI native, RE-API simulated |

\* Box queries simulated by calculating bounding circle, fetching data, then filtering to box bounds

## Usage Examples

### Basic Usage with Auto Backend Selection

```python
from skysnoop import SkySnoop

async with SkySnoop(backend="auto") as client:
    # Prefers RE-API if accessible, falls back to OpenAPI
    # Uses OpenAPI if API key is provided (for future compatibility)
    response = await client.get_by_hex("abc123")
    print(f"Found {response.count} aircraft from {response.backend} backend")

    for aircraft in response:
        print(f"{aircraft.hex}: {aircraft.callsign}")
```

### Explicit Backend Selection

```python
# Force OpenAPI backend
async with SkySnoop(backend="openapi", api_key="your-key") as client:
    response = await client.get_by_hex("abc123")

# Force RE-API backend
async with SkySnoop(backend="reapi") as client:
    response = await client.get_by_hex("abc123")
```

### Migration from Existing Client

```python
# Before (OpenAPI-specific)
from skysnoop.client import OpenAPIClient

async with OpenAPIClient() as client:
    response = await client.v2.get_by_hex("abc123")
    print(f"Found {response.total} aircraft")

# After (backend-agnostic)
from skysnoop import SkySnoop

async with SkySnoop(backend="auto") as client:
    response = await client.get_by_hex("abc123")
    print(f"Found {response.count} aircraft")
```

### Handling Backend-Specific Features

```python
async with SkySnoop(backend="auto") as client:
    # Box queries work with both backends
    # OpenAPI: simulated via circle + client-side filtering
    # RE-API: native support
    response = await client.get_in_box(
        lat_south=37.0, lat_north=38.0,
        lon_west=-123.0, lon_east=-122.0
    )

    # Check if operation was simulated
    if hasattr(response, 'simulated') and response.simulated:
        print(f"Note: Results from simulated operation via {response.backend}")
        print("For optimal performance with box queries, consider backend='reapi'")
```

### Implementation Phases

1. **Phase 1**: Core foundation (exceptions, SkyData, BackendProtocol)
2. **Phase 2**: Backend adapters (OpenAPIAdapter, ReAPIAdapter) with tests
3. **Phase 3**: SkySnoop client with backend selection logic and tests
4. **Phase 4**: Documentation and polish
5. **Phase 5**: Integration testing and coverage verification
6. **Phase 6**: CLI integration

See `tasks.md` for detailed task breakdown with validation checklist.

## Testing Strategy

### Protocol-Based Shared Test Suite (DRY)

Since all adapters implement `BackendProtocol`, use a **single shared test suite**:

- **Shared Protocol Tests**: Parameterized test class that validates BackendProtocol compliance
  - Run identical tests against OpenAPIAdapter, ReAPIAdapter, and any future adapters
  - Verify all protocol methods, signatures, return types, and async behavior
  - Test common error handling and response conversion patterns
  - Prevents test duplication and ensures consistent behavior across adapters

- **Adapter-Specific Tests**: Only test unique implementation details
  - OpenAPIAdapter: V2ResponseModel conversion, simulation logic, API key handling
  - ReAPIAdapter: APIResponse conversion, native RE-API operations
  - Focus on edge cases not covered by shared protocol tests

- **SkySnoop Client Tests**: Backend selection logic and delegation
- **Integration Tests**: Optional tests with real APIs when available
- **Type Safety**: Verify protocol compliance with mypy
- **Backward Compatibility**: Ensure all existing tests pass unchanged

**Benefits**: Adding new backends is trivial—they automatically inherit the full test suite. Tests stay DRY and maintainable.

Target: >90% code coverage for all new code

## Backward Compatibility

**Zero Breaking Changes**:

- All existing `ReAPIClient` usage continues to work unchanged
- All existing `OpenAPIClient` usage continues to work unchanged
- All existing import paths remain valid
- No modifications to existing client public APIs
- New unified interface is purely additive

Users can adopt SkySnoop:

- Immediately for new projects (recommended)
- Incrementally for existing projects
- Never (continue using direct OpenAPIClient/ReAPIClient)

## Success Criteria

- [ ] SkySnoop provides consistent interface across both backends as primary user-facing API
- [ ] Backend selection works automatically with sensible defaults
- [ ] All common operations mapped and tested for both backends
- [ ] Unsupported operations raise clear, helpful errors
- [ ] Response normalization works correctly for both backends
- [ ] Type checking passes with mypy (Protocol compliance verified)
- [ ] Test coverage >90% for all new code
- [ ] All existing tests pass (backward compatibility maintained)
- [ ] Documentation updated with examples and method mapping
- [ ] README includes SkySnoop usage guide as primary interface

## Related Work

- **OpenSpec Spec**: New spec `unified-client` defined in `specs/unified-client/spec.md`
- **Related Specs**:
  - `api-client`: Defines existing OpenAPIClient and ReAPIClient
  - `aircraft-data-models`: Defines Aircraft model used in responses
  - `query-filtering`: Defines QueryFilters used with RE-API

## Open Questions

1. **Filter Compatibility**: How to handle filters that work differently between APIs?
   - **Answer**: Pass QueryFilters through ReAPIAdapter unchanged; ignore in OpenAPIAdapter with warning log

2. **Bulk Operations**: How to handle operations that don't exist in OpenAPI?
   - **Answer**: Raise `UnsupportedOperationError` with message indicating feature is RE-API only

3. **V0 Endpoints**: Should unified interface support v0 endpoints?
   - **Answer**: No, users access these via `client.v0` directly on OpenAPIClient

4. **Type Annotations**: Should methods return `SkyData` or use generics?
   - **Answer**: Use concrete `SkyData` type for simplicity

## Alternatives Considered

See `design.md` section "Alternatives Considered" for detailed analysis of:

- Creating a third implementation (rejected: maintenance burden)
- Modifying existing clients to share interface (rejected: breaking changes)
- Using ABC instead of Protocol (rejected: prefer Protocol for type checking)
- Single unified response without aircraft conversion (rejected: defeats purpose)

## Dependencies

- No new external dependencies required
- Uses existing: `pydantic`, `httpx`, `typing.Protocol`
- Builds on existing: `ReAPIClient`, `OpenAPIClient`, `Aircraft`, `APIResponse`, `V2ResponseModel`

## Timeline Estimate

- Phase 1-2: 2-3 days (core foundation and adapters)
- Phase 3: 1-2 days (unified client and backend selection)
- Phase 4-5: 1-2 days (documentation and testing)
- Phase 6: 1 day (CLI integration)

**Total**: 6-9 days for full implementation with comprehensive testing and documentation

## Approval

This proposal should be reviewed by:

- Project maintainer
- Potential early adopters for feedback on API design
- Type checking validation (ensure Protocol approach works as expected)

After approval, implementation will proceed according to `tasks.md` checklist.
