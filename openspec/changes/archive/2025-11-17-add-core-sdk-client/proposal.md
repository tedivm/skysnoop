# Change: Add Core SDK Client

## Why

The adsblol project currently has only scaffolding (settings, CLI framework) but lacks the core functionality to interact with the adsb.lol re-api. Users need a production-ready, typed, async-first Python client library to query aircraft data, apply filters, and access telemetry through both library and CLI interfaces.

## What Changes

- Add Pydantic data models for Aircraft and APIResponse with full type safety and validation
- Implement async HTTP client using httpx for all API communication
- Create query builder supporting all adsb.lol query types (circle, closest, box, find_hex, find_callsign, find_reg, find_type, all_with_pos, all)
- Add comprehensive filtering system (altitude, type, callsign, squawk, database flags)
- Extend CLI with commands for all query types and filters
- Add custom exception classes for clear error handling
- Include comprehensive test suite with >90% coverage
- Add httpx dependency to pyproject.toml

## Impact

**Affected specs:**

- Creates new capability: `aircraft-data-models`
- Creates new capability: `api-client`
- Creates new capability: `query-filtering`
- Creates new capability: `cli-commands`

**Affected code:**

- New: `adsblol/models/aircraft.py` - Aircraft data model
- New: `adsblol/models/response.py` - API response model
- New: `adsblol/client/base.py` - Base HTTP client
- New: `adsblol/client/api.py` - High-level API client
- New: `adsblol/query/builder.py` - Query parameter builder
- New: `adsblol/query/filters.py` - Filter definitions
- New: `adsblol/exceptions.py` - Custom exceptions
- Modified: `adsblol/cli.py` - Add query commands
- Modified: `adsblol/conf/settings.py` - Add API settings
- Modified: `pyproject.toml` - Add httpx dependency
- New: Comprehensive test suite in `tests/`
- New: `tests/fixtures/api_responses/` - Real API response data for testing
- New: `tests/fixtures/README.md` - Documentation for fixture creation
- Modified: `README.md` - Add usage documentation

---

## Extended Details

### Goals

- **Production Ready**: Implement fully functional SDK with no stubs or development-only logic
- **Type Safe**: Provide comprehensive type hints and Pydantic models for all API data
- **Async First**: Use httpx for async HTTP operations throughout
- **Developer Friendly**: Intuitive API with clear documentation and examples
- **CLI Support**: Expose key functionality through typer commands for quick queries
- **Testable**: Include comprehensive test coverage for all components

### Non-Goals

- **Authentication**: API uses IP-based access control only
- **Caching**: Defer to future enhancement (use API directly for now)
- **Rate Limiting**: Implement basic timeouts but defer sophisticated rate limiting
- **WebSocket Support**: Stick to HTTP API for initial release
- **Data Persistence**: No local database or storage layer
- **Advanced Filtering**: Complex filter combinations can be added later
- **Mock Server**: Tests will use response mocking, not full server simulation

### Testing Requirements

**CRITICAL**: All mock data for tests MUST come from real API responses. When writing tests, the developer must:

1. Call the real adsb.lol API while they have access to it
2. Capture actual API responses for each query type and scenario
3. Save these responses as mock data fixtures in the test suite
4. Use the captured real data for all mocked HTTP responses in tests

This ensures tests use realistic data structures and edge cases from the actual API, while allowing tests to run in environments (like GitHub Actions) where the API is not accessible due to IP restrictions. Mock data should be stored in `tests/fixtures/` as JSON files.

**Live API Testing**: In addition to fixture-based tests, the SDK should support optional integration tests against the live API when available:

1. Add pytest markers (e.g., `@pytest.mark.live_api`) for tests requiring live API access
2. Skip live API tests by default; run with `pytest --run-live-api` when developer has access
3. Use environment variable or config to provide feeder credentials/IP when testing live
4. This allows:
   - Developers with API access to validate against real, current data
   - Continuous validation that fixtures remain representative
   - Detection of API schema changes or behavior updates
   - Verification that URL encoding and query construction work correctly

Live API tests will be implemented in future phases as integration tests.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API schema changes | Medium | Use flexible Pydantic models with `extra="allow"` for forward compatibility |
| IP access restrictions | Low | Document clearly in README; provide clear error messages |
| Missing/stale data | Medium | Make all aircraft fields optional with proper defaults |
| Breaking changes | Low | Use semantic versioning; this is v0.x so breaking changes expected |
| URL encoding breaks API | High | Build query strings manually; do NOT use httpx params dict which encodes commas |

## Open Questions

1. **Default timeout values**: What should be the default HTTP timeout? (Suggested: 30 seconds)
2. **Retry behavior**: Should the client auto-retry on transient failures? (Suggested: No, let users implement retry logic)
3. **API base URL**: Should this be configurable via settings? (Suggested: Yes, with default to `https://re-api.adsb.lol/`)
4. **Result pagination**: Does the API support pagination? (Answer: No, results are atomic)

## Alternatives Considered

### Alternative 1: Sync-only client

**Rejected**: Project requirements specify async-first approach for high-performance applications.

### Alternative 2: Use requests instead of httpx

**Rejected**: httpx provides async support and is the modern choice for async HTTP operations.

### Alternative 3: Minimal data model (dict-based)

**Rejected**: Strong typing is a core project goal and provides better developer experience.

## Timeline

- **Week 1**: Implement data models and basic client structure
- **Week 2**: Complete query builder and filtering capabilities
- **Week 3**: Add CLI commands and comprehensive tests
- **Week 4**: Documentation and examples

## Success Criteria

- [ ] All query types (circle, closest, box, find_*, all) are implemented
- [ ] All filters (altitude, type, callsign, etc.) are supported
- [ ] Complete test coverage (>90%) for all new code
- [ ] Type checking passes with mypy --strict
- [ ] CLI can perform basic queries (circle, find_hex, all)
- [ ] README includes installation, usage examples, and API reference
- [ ] No production-only stubs or placeholder logic
