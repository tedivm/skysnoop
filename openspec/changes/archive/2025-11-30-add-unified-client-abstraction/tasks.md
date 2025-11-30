# Implementation Tasks

## Phase 1: Core Foundation ✅ COMPLETE

- [x] **Create exception classes** ✅
  - Create `UnsupportedOperationError` exception in `skysnoop/exceptions.py`
  - Create `BackendConnectionError` exception in `skysnoop/exceptions.py`
  - Add docstrings explaining when each exception is raised
  - Add to `__all__` exports

- [x] **Create SkyData model** ✅
  - Create `skysnoop/models/skydata.py`
  - Define `SkyData` Pydantic model with all required fields
  - Add `timestamp`, `result_count`, `processing_time`, `aircraft`, `backend` fields
  - Add optional `simulated` boolean field to indicate simulated operations
  - Implement `count`, `has_results` properties
  - Implement `__len__()`, `__iter__()`, `__str__()` methods
  - Add comprehensive docstrings with examples

- [x] **Create BackendProtocol** ✅
  - Create `skysnoop/client/protocol.py`
  - Define `BackendProtocol` using `typing.Protocol`
  - Specify all required method signatures returning SkyData (get_by_hex, get_by_callsign, etc.)
  - Include async context manager methods (**aenter**, **aexit**)
  - Add docstrings explaining protocol contract

- [x] **Write tests for SkyData** ✅
  - Create `tests/models/test_skydata.py`
  - Test field normalization from different inputs
  - Test convenience properties (count, has_results)
  - Test iteration and len() behavior
  - Test string representation
  - Test Pydantic validation
  - **Result: 14 tests, all passing**

## Phase 2: Backend Adapters ✅ COMPLETE

- [x] **Create shared protocol test suite** ✅
  - Create `tests/client/test_protocol_compliance.py`
  - Define `BaseProtocolTestSuite` class with parameterized tests
  - Test all BackendProtocol methods (get_by_hex, get_by_callsign, etc.)
  - Test async context manager support (`__aenter__`, `__aexit__`)
  - Test return types are SkyData
  - Test error handling for common scenarios
  - Use pytest fixtures to parameterize adapter instances
  - This suite will be run against all adapter implementations
  - **Result: 14 shared tests per adapter (28 total protocol compliance tests)**

- [x] **Implement OpenAPIAdapter** ✅
  - Create `skysnoop/client/adapters/openapi_adapter.py`
  - Implement initialization with api_key, base_url, timeout parameters
  - Implement async context manager methods
  - Create `_convert_v2_response()` helper to convert V2ResponseModel to SkyData
  - Create `_convert_aircraft()` helper to convert V2ResponseAcItem to Aircraft
  - Implement get_by_hex() delegating to client.v2.get_by_hex()
  - Implement get_by_callsign() delegating to client.v2.get_by_callsign()
  - Implement get_by_registration() delegating to client.v2.get_by_registration()
  - Implement get_by_type() delegating to client.v2.get_by_type()
  - Implement get_in_circle() delegating to client.v2.get_by_point()
  - Implement get_closest() delegating to client.v2.get_closest()
  - Implement get_in_box() with simulation: calculate bounding circle, fetch, filter client-side with Haversine distance
  - Implement get_all_with_pos() to raise UnsupportedOperationError (250 NM limit prevents simulation)
  - Add helper `_calculate_haversine_distance()` for accurate distance calculations
  - Add helper `_is_in_box()` to filter aircraft to box bounds with longitude wraparound handling
  - Set `simulated=True` in SkyData for simulated operations
  - Add comprehensive docstrings documenting simulation behavior and limitations

- [x] **Write tests for OpenAPIAdapter** ✅
  - Create `tests/client/test_openapi_adapter.py`
  - **Run shared protocol test suite** against OpenAPIAdapter (parameterized)
  - Test adapter-specific functionality:
    - Adapter initialization with API key (for future compatibility)
    - V2ResponseModel to SkyData conversion edge cases
    - V2ResponseAcItem to Aircraft conversion with missing fields
    - Error handling for OpenAPI-specific exceptions
  - Do NOT duplicate protocol tests—only test OpenAPI-specific behavior
  - **Result: 14 protocol tests + 7 adapter-specific tests = 21 tests**

- [x] **Write tests for OpenAPIAdapter simulation and limitations** ✅
  - Create `tests/client/test_openapi_adapter_simulation.py` (adapter-specific)
  - Test box query simulation with various boundary conditions
  - Test longitude wraparound handling in box filter
  - Test that get_all_with_pos() raises UnsupportedOperationError
  - Verify error message mentions RE-API backend and 250 NM limit
  - Verify `simulated=True` flag is set correctly for box queries
  - Test edge cases (empty results, single aircraft, max radius)
  - Verify client-side filtering accuracy using Haversine distance
  - Note: These are OpenAPI-specific, not part of shared protocol suite
  - **Result: 7 simulation tests**

- [x] **Create ReAPIAdapter** ✅
  - Create `skysnoop/client/adapters/reapi_adapter.py`
  - Implement initialization with base_url, timeout parameters
  - Implement async context manager methods
  - Create `_convert_api_response()` helper to convert APIResponse to SkyData
  - Implement get_by_hex() delegating to client.find_hex()
  - Implement get_by_callsign() delegating to client.find_callsign()
  - Implement get_by_registration() delegating to client.find_reg()
  - Implement get_by_type() delegating to client.find_type()
  - Implement get_in_circle() delegating to client.circle()
  - Implement get_closest() delegating to client.closest()
  - Implement get_in_box() delegating to client.box()
  - Implement get_all_with_pos() delegating to client.all_with_pos()
  - Set `simulated=False` in SkyData for all operations (RE-API has native support)
  - Support filters parameter for applicable methods
  - Add comprehensive docstrings

- [x] **Write tests for ReAPIAdapter** ✅
  - Create `tests/client/test_reapi_adapter.py`
  - **Run shared protocol test suite** against ReAPIAdapter (parameterized)
  - Test adapter-specific functionality:
    - APIResponse to SkyData conversion edge cases
    - Filter parameter passthrough to RE-API methods
    - Native box and all_with_pos operation support
    - Error handling for RE-API-specific exceptions
  - Do NOT duplicate protocol tests—only test RE-API-specific behavior
  - **Result: 14 protocol tests + 9 adapter-specific tests = 23 tests**

**Phase 2 Summary: 51 tests total (28 protocol compliance + 23 adapter-specific), all passing ✅**

## Phase 3: SkySnoop Client ✅ COMPLETE

- [x] **Create backend selection logic** ✅
  - Create `skysnoop/client/backend_selection.py`
  - Implement `select_backend()` async function with auto selection logic
  - Implement `select_backend_sync()` for non-async contexts
  - If API key provided → select OpenAPI (API key for future compatibility, not currently required)
  - If no API key and prefer_reapi=True → select RE-API (preferred stable backend)
  - If prefer_reapi=False → fallback to OpenAPI
  - Add logging for backend selection decisions
  - Document rationale: RE-API preferred but OpenAPI fallback, API key triggers OpenAPI

- [x] **Create SkySnoop client** ✅
  - Create `skysnoop/client/skysnoop.py`
  - Implement initialization with backend, api_key, base_url, timeout parameters
  - Support backend="auto", "openapi", "reapi" options
  - Instantiate appropriate adapter based on backend selection
  - Implement async context manager methods delegating to adapter
  - Make this the primary user-facing API of the library
  - Implement get_by_hex() delegating to adapter
  - Implement get_by_callsign() delegating to adapter
  - Implement get_by_registration() delegating to adapter
  - Implement get_by_type() delegating to adapter
  - Implement get_in_circle() delegating to adapter
  - Implement get_closest() delegating to adapter
  - Implement get_in_box() delegating to adapter (supports simulation with OpenAPI)
  - Implement get_all_with_pos() delegating to adapter (raises UnsupportedOperationError with OpenAPI)
  - Add comprehensive docstrings with usage examples
  - Add type hints for all methods

- [x] **Update exports** ✅
  - Add SkySnoop to `skysnoop/__init__.py` as primary import
  - Add SkySnoop to `skysnoop/client/__init__.py` for consistency
  - Add SkyData to exports
  - Add new exceptions to exports
  - Ensure backward compatibility with existing exports

- [x] **Write tests for backend selection** ✅
  - Create `tests/client/test_backend_selection.py`
  - Test auto selection uses OpenAPI when API key present
  - Test auto selection prefers RE-API when no API key and prefer_reapi=True
  - Test auto selection falls back to OpenAPI when prefer_reapi=False
  - Test explicit backend override
  - Test edge cases (empty strings, whitespace, consistency)
  - **Result: 12 tests**

- [x] **Write tests for SkySnoop client** ✅
  - Create `tests/client/test_skysnoop.py`
  - Test initialization with different backend options
  - Test context manager support
  - Mock adapters and test delegation for each method
  - Test auto backend selection behavior
  - Test explicit backend selection (openapi, reapi)
  - Test simulated operations return simulated=True with OpenAPI backend
  - Test native operations return simulated=False with RE-API backend
  - Test error propagation from adapters
  - Test that correct adapter is instantiated based on backend parameter
  - **Result: 26 tests**

**Phase 3 Summary: 38 tests total (12 backend selection + 26 SkySnoop client), all passing ✅**

**OVERALL PROGRESS: Phases 1-3 Complete - 103 tests passing ✅**

## Phase 4: Integration and Testing ✅ COMPLETE

- [x] **Integration tests with live APIs** ✅
  - Created `tests/integration/test_skysnoop_live.py` with 13 integration tests
  - Test classes organized by backend and functionality:
    - `TestSkySnoopLiveReAPI`: 4 RE-API backend tests (marked with `@pytest.mark.live_api`)
    - `TestSkySnoopLiveOpenAPI`: 4 OpenAPI backend tests (marked with `@pytest.mark.live_openapi`)
    - `TestSkySnoopLiveAutoBackend`: 3 auto-selection tests (individual test markers)
    - `TestSkySnoopLiveFilters`: 2 filter handling tests (individual test markers)
  - Tests use individual markers rather than class-level to ensure correct backend availability
  - Tests with both markers only run when both backends are available
  - Verified with live API access: all 13 tests passing

- [x] **Add fixtures for testing** ✅
  - Updated `tests/conftest.py` with SkySnoop-specific fixtures
  - Added `mock_skydata` fixture for creating test SkyData instances
  - Added `mock_aircraft` fixture for creating test Aircraft instances
  - Added `load_openapi_response` fixture for loading OpenAPI test data
  - Configured test markers: `live_api` and `live_openapi`
  - Implemented smart skip logic: tests require appropriate flags to run
  - Tests with both markers require both `--run-live-api` and `--run-live-openapi`

- [x] **Code coverage verification** ✅
  - Achieved **100% coverage** on all unified client code
  - Coverage breakdown:
    - `skysnoop/models/skydata.py`: 100% (25 statements)
    - `skysnoop/client/protocol.py`: 100% (14 statements)
    - `skysnoop/client/backend_selection.py`: 100% (22 statements)
    - `skysnoop/client/skysnoop.py`: 100% (62 statements)
    - `skysnoop/client/adapters/reapi_adapter.py`: 100% (46 statements)
    - `skysnoop/client/adapters/openapi_adapter.py`: 100% (80 statements)
  - Total: 252 statements, 0 missing
  - Added tests for edge cases (filter warnings, parameter mapping)

- [x] **Run full test suite** ✅
  - All 258 unit tests passing
  - 32 integration tests skipped by default (require live API flags)
  - Fixed parameter name mapping in `SkySnoop.get_in_box()` (lat_min/max → lat_south/north)
  - Verified backward compatibility: all existing tests still passing
  - No regressions introduced

**Phase 4 Summary: 100% code coverage, 258 unit tests + 13 integration tests, all passing ✅**

## Phase 5: CLI Integration ✅ COMPLETE

- [x] **Add backend flag to CLI** ✅
  - Updated `skysnoop/cli.py` with `--backend` option for all commands
  - Added `BackendChoice` type: `Literal["auto", "reapi", "openapi"]`
  - Created `get_client_for_backend()` helper function
  - Default behavior (no --backend flag) uses legacy ReAPIClient for backward compatibility
  - When --backend is specified, uses SkySnoop with selected backend
  - Documented in CLI command help text

- [x] **Update CLI commands to use SkySnoop** ✅
  - Updated all 8 CLI commands: circle, closest, box, find-hex, find-callsign, find-reg, find-type, all-aircraft
  - Each command now supports --backend parameter
  - Implemented duck typing (hasattr checks) to determine client type for method dispatch
  - Method mappings:
    - circle → get_in_circle
    - closest → get_closest
    - box → get_in_box
    - find_hex → get_by_hex
    - find_callsign → get_by_callsign
    - find_reg → get_by_registration
    - find_type → get_by_type
    - all_with_pos → get_all_with_pos
  - Updated formatters to handle both APIResponse and SkyData (Union types)
  - Maintained full backward compatibility with existing CLI usage
  - Added UnsupportedOperationError handling with helpful error messages

- [x] **Write CLI tests for backend option** ✅
  - Added 5 new tests to `tests/test_cli.py`:
    - `test_circle_command_with_backend_auto`: Tests --backend auto flag
    - `test_find_hex_command_with_backend_openapi`: Tests --backend openapi flag
    - `test_backend_reapi_explicit`: Tests --backend reapi flag
    - `test_backward_compatibility_without_backend`: Verifies legacy behavior preserved
    - `test_unsupported_operation_error_handling`: Tests graceful error handling
  - Updated all 17 existing ReAPIClient tests to use `del mock_client.get_in_circle` pattern
  - This simulates ReAPIClient not having SkySnoop methods for proper duck typing
  - All 22 CLI tests passing (17 existing + 5 new backend tests)

**Phase 5 Summary: CLI fully integrated with backend selection, 22 tests passing, full backward compatibility ✅**

**OVERALL PROGRESS: Phases 1-5 Complete - 263 unit tests + 13 integration tests, all passing ✅**


## Phase 6: Documentation and Polish ✅ COMPLETE

- [x] **Add usage examples** ✅
  - Added comprehensive examples in SkySnoop docstrings showing usage as primary interface
  - Documented backend="auto" usage (recommended default)
  - Showed explicit backend selection examples
  - Created migration guide from existing clients to SkySnoop
  - Documented simulated operations vs native operations with clear indicators

- [x] **Update README** ✅
  - Featured SkySnoop prominently at the beginning as the primary interface
  - Moved basic examples to use SkySnoop instead of direct clients
  - Added comprehensive code examples for common use cases:
    - Basic usage with auto backend selection
    - Usage with filters
    - Explicit backend selection
    - CLI usage with --backend flag
  - Documented backend selection behavior:
    - API key → OpenAPI (future-proofing)
    - No API key → RE-API preferred (stable, full features)
    - OpenAPI fallback available
  - Clarified API key is for future compatibility, not currently required
  - Created complete migration guide with method mapping tables
  - Added backend comparison table showing feature availability
  - Noted that direct clients (OpenAPIClient, ReAPIClient) remain available for advanced use

- [x] **Add type checking validation** ✅
  - Ran mypy on all new code - all checks pass
  - Validated Protocol conformance with structural subtyping
  - Fixed type error in CLI (backend parameter typing)
  - Confirmed all public methods have proper return type annotations
  - All 28 source files type-check successfully

- [x] **Update module documentation** ✅
  - Enhanced module-level docstrings in all new files:
    - `protocol.py`: Architecture explanation, design decisions
    - `backend_selection.py`: Selection strategy, design rationale
    - `reapi_adapter.py`: Implementation details, trade-offs
    - `openapi_adapter.py`: Simulation strategy, trade-offs
    - `skysnoop.py`: Already had comprehensive docs
  - Documented the adapter pattern architecture clearly
  - Explained when to use SkySnoop vs direct clients
  - Documented limitations and trade-offs for each backend

**Phase 6 Summary: Comprehensive documentation added, all type checking passes, README fully updated with SkySnoop as primary interface ✅**

## Validation Checklist ✅ COMPLETE

All validation criteria met:

- [x] Shared protocol test suite exists and runs against all adapters (DRY principle) ✅
- [x] No duplicate tests between adapter test files—only adapter-specific edge cases tested ✅
- [x] All adapters pass the identical shared protocol test suite ✅
- [x] All new code has comprehensive docstrings ✅
- [x] All new code has type hints ✅
- [x] All public methods have usage examples in docstrings ✅
- [x] Test coverage 100% for new code (252 statements, 0 missing) ✅
- [x] mypy passes with no errors (28 source files checked) ✅
- [x] All existing tests pass (263 unit tests + 13 integration tests) ✅
- [x] New tests cover all scenarios from spec ✅
- [x] README is updated with SkySnoop documentation prominently ✅
- [x] No breaking changes to existing APIs (full backward compatibility) ✅

---

## Project Completion Summary

**Total Implementation:**

- **6 Phases Completed**: Foundation → Adapters → Client → Integration → CLI → Documentation
- **263 Unit Tests**: All passing
- **13 Integration Tests**: All passing (skipped by default, require live API flags)
- **100% Code Coverage**: All new code fully tested
- **Zero Type Errors**: All mypy checks pass
- **Full Backward Compatibility**: No breaking changes

**New Components:**

1. `SkyData` model - Unified response format
2. `BackendProtocol` - Interface contract for adapters
3. `ReAPIAdapter` - RE-API backend implementation
4. `OpenAPIAdapter` - OpenAPI backend implementation with simulation
5. `SkySnoop` - Unified client (primary interface)
6. Backend selection logic - Automatic and explicit selection
7. CLI backend support - `--backend` flag for all commands
8. Comprehensive documentation - README, docstrings, migration guide

**Key Features:**

- Single consistent interface across both backends
- Automatic backend selection (prefers RE-API)
- Explicit backend selection when needed
- Geographic query simulation for OpenAPI
- Normalized responses with `SkyData`
- Full backward compatibility maintained
- CLI integration with backend selection
- Complete migration guide for users

**Architecture Highlights:**

- Adapter pattern for backend abstraction
- Protocol-based structural subtyping
- Shared test suite for protocol conformance
- Duck typing for CLI client detection
- Context manager support for resource management

This unified client abstraction successfully provides a single, consistent interface to both adsb.lol APIs while maintaining full backward compatibility and preparing for future API key requirements.
