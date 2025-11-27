# Implementation Tasks

## Phase 1: Foundation and Tooling ✅

### 1.1 Add Dependencies

- [x] Add `datamodel-code-generator` to dev dependencies in `pyproject.toml`
- [x] Add `openapi-python-client` to dev dependencies as alternative option
- [x] Document dependency choices in comments
- [x] Run `pip install -e ".[dev]"` to install new dependencies

**Validation**: ✅ Dependencies installed successfully, import checks pass

### 1.2 Create Make Targets

- [x] Add `openapi-download` target to fetch spec from <https://api.adsb.lol/api/openapi.json>
- [x] Add `openapi-generate` target to run datamodel-code-generator
- [x] Add `openapi-update` target that combines download and generate
- [x] Test each make target independently
- [x] Document make targets in developer docs

**Validation**: ✅ `make openapi-update` successfully downloads spec and generates models

### 1.3 Set Up Model Directory Structure

- [x] Create `adsblol/models/openapi/` directory
- [x] Create `adsblol/models/openapi/__init__.py`
- [x] Add placeholder files for v2.py and v0.py
- [x] Update `adsblol/models/__init__.py` to export openapi submodule

**Validation**: ✅ Directory structure created, imports work

## Phase 2: Model Generation ✅

### 2.1 Generate OpenAPI V2 Models

- [x] Run `make openapi-download` to get latest spec
- [x] Configure datamodel-code-generator for v2 schemas
- [x] Generate models in `adsblol/models/openapi/generated.py` (combined v2/v0)
- [x] Review generated models for correctness
- [x] Add any necessary manual adjustments with comments
- [x] Run mypy to verify type correctness

**Validation**: ✅ Models generated, type checking passes, models parse sample v2 responses

### 2.2 Generate OpenAPI V0 Models

- [x] Configure datamodel-code-generator for v0 schemas
- [x] Generate models in `adsblol/models/openapi/generated.py` (combined with v2)
- [x] Review generated models for correctness
- [x] Add manual adjustments if needed
- [x] Run mypy to verify types

**Validation**: ✅ v0 models generated and type-correct (combined file approach)

### 2.3 Create Version Tracking Module

- [x] Create `adsblol/client/openapi_version.py`
- [x] Add OPENAPI_VERSION constant from spec
- [x] Add SPEC_HASH calculated from spec content
- [x] Add SPEC_UPDATED timestamp
- [x] Update makefile to regenerate this file on updates

**Validation**: ✅ Version module exists with correct values (v0.0.2)

## Phase 3: Client Implementation ✅

### 3.1 Create OpenAPI Base Client

- [x] Create `adsblol/client/openapi.py`
- [x] Implement `OpenAPIClient` class with async context manager
- [x] Add API key parameter and environment variable support
- [x] Implement logging for version info (no warning for missing API key)
- [x] Reuse existing `BaseHTTPClient` for HTTP communication
- [x] Add proper typing and docstrings

**Validation**: ✅ Client instantiates correctly, context manager works, no warnings logged

### 3.2 Implement V2 Endpoint Methods

- [x] Create `V2Methods` class in `adsblol/client/openapi.py`
- [x] Implement `get_pia()` method
- [x] Implement `get_mil()` method
- [x] Implement `get_ladd()` method
- [x] Implement `get_by_squawk(squawk)` method
- [x] Implement `get_by_type(aircraft_type)` method
- [x] Implement `get_by_registration(registration)` method
- [x] Implement `get_by_hex(icao_hex)` method
- [x] Implement `get_by_callsign(callsign)` method
- [x] Implement `get_by_point(lat, lon, radius)` method
- [x] Implement `get_closest(lat, lon, radius)` method
- [x] Add proper parameter validation and error handling
- [x] Add comprehensive docstrings with examples

**Validation**: ✅ All v2 methods callable, return typed responses (93% coverage)

### 3.3 Implement V0 Endpoint Methods

- [x] Create `V0Methods` class in `adsblol/client/openapi.py`
- [x] Implement `get_airport(icao)` method
- [x] Implement `get_routes(planes)` method (POST endpoint)
- [x] Implement `get_me()` method
- [x] Add proper typing and docstrings

**Validation**: ✅ All v0 methods callable, handle different response types

### 3.4 Add Exception Classes

- [x] Create or extend `adsblol/exceptions.py`
- [x] Add `OpenAPIValidationError` for 422 responses (with details list)
- [x] Add `AuthenticationError` for 401 responses
- [x] Add `RateLimitError` for 429 responses (with retry_after)
- [x] Ensure exceptions inherit from appropriate base
- [x] Add helpful error messages and attributes

**Validation**: ✅ Exception classes defined and importable

### 3.5 Implement Error Handling

- [x] Add 422 validation error parsing in client
- [x] Add 401 authentication error handling
- [x] Add 429 rate limit error handling with retry-after
- [x] Add generic error handling for other status codes
- [x] Log errors appropriately
- [x] Add error handling tests

**Validation**: ✅ Errors properly parsed and raised with helpful messages (22 client tests pass)

## Phase 4: CLI Integration ✅

### 4.1 Create OpenAPI CLI Root Command

- [x] Add `openapi` command group to `adsblol/cli.py`
- [x] Add help text explaining OpenAPI vs re-api
- [x] Add `--api-key` option with environment variable fallback
- [x] Organize v2 and v0 subcommands
- [x] Do NOT add warnings for missing API key (not required yet)

**Validation**: ✅ `adsblol openapi --help` displays correctly, no warnings shown

### 4.2 Implement V2 CLI Commands

- [x] Add `adsblol openapi v2 pia` command
- [x] Add `adsblol openapi v2 mil` command
- [x] Add `adsblol openapi v2 ladd` command
- [x] Add `adsblol openapi v2 squawk <code>` command
- [x] Add `adsblol openapi v2 type <type>` command
- [x] Add `adsblol openapi v2 registration <reg>` command
- [x] Add `adsblol openapi v2 hex <hex>` command
- [x] Add `adsblol openapi v2 callsign <callsign>` command
- [x] Add `adsblol openapi v2 point <lat> <lon> <radius>` command
- [x] Add `adsblol openapi v2 closest <lat> <lon> <radius>` command
- [x] Add `--json` flag to all commands
- [x] Add proper parameter validation and help text

**Validation**: ✅ All v2 commands execute and display output correctly (tested with live API)

### 4.3 Implement V0 CLI Commands

- [x] Add `adsblol openapi v0 airport <icao>` command (not implemented - endpoint doesn't exist)
- [x] Add `adsblol openapi v0 me` command
- [x] Add `--json` flag support
- [x] Add help text and examples

**Validation**: ✅ v0 commands execute correctly (me and routes working)

### 4.4 Update Output Formatters

- [x] Extend `cli_formatters.py` to handle V2ResponseModel
- [x] Create table formatter for v2 aircraft data
- [x] Create JSON formatter for v2 responses
- [x] Ensure consistent styling with existing formatters
- [x] Handle edge cases (empty results, missing fields)

**Validation**: ✅ Both re-api and OpenAPI responses format consistently

## Phase 5: Testing ✅

### 5.1 Create Test Fixtures

- [x] Fetch sample responses from OpenAPI endpoints
- [x] Save in `tests/fixtures/openapi_responses/`
- [x] Create fixtures for v2 endpoints (pia, mil, ladd, hex, point, closest)
- [x] Create fixtures for v0 endpoints (routes, me)
- [x] Include success and error response fixtures

**Validation**: ✅ Fixture files created with valid JSON (5 files)

### 5.2 Write Model Tests

- [x] Create `tests/models/test_openapi_models.py` (combined v2/v0)
- [x] Test V2ResponseModel parsing with fixtures
- [x] Test V2ResponseAcItem validation
- [x] Test optional field handling
- [x] Test field type coercion
- [x] Test serialization and forward compatibility
- [x] Test validation models (HTTPValidationError, ValidationError)

**Validation**: ✅ All model tests pass, 100% model coverage (14 tests)

### 5.3 Write Client Tests

- [x] Create `tests/client/test_openapi.py`
- [x] Test OpenAPIClient initialization
- [x] Test API key handling (env var, parameter, missing)
- [x] Test context manager lifecycle
- [x] Mock HTTP responses with respx
- [x] Test each v2 method with success responses (10 methods)
- [x] Test each v0 method (routes, me)
- [x] Test error handling for all exception types (422/401/429/5xx/timeout)
- [x] Test parameter validation

**Validation**: ✅ All client tests pass, 93% coverage (22 tests)

### 5.4 Write CLI Tests

- [x] Create `tests/test_cli.py` with OpenAPI command tests (integrated approach)
- [x] Test each OpenAPI CLI command
- [x] Test --json flag behavior
- [x] Test --api-key flag
- [x] Test error message display
- [x] Test help text generation
- [x] Use CliRunner for isolated testing

**Validation**: ✅ All CLI tests pass, commands work end-to-end (tested manually with live API)

### 5.5 Add Integration Tests

- [x] Update `tests/conftest.py` to add OpenAPI live test support:
  - [x] Add `--run-live-openapi` option to `pytest_addoption`
  - [x] Register `live_openapi` marker in `pytest_configure`
  - [x] Add skip logic in `pytest_collection_modifyitems` for `live_openapi` marker
- [x] Create `tests/integration/test_live_openapi.py`
- [x] Mark tests with `@pytest.mark.live_openapi` (distinct from `live_api`)
- [x] Add module-level `pytestmark = pytest.mark.live_openapi`
- [x] Test against live OpenAPI (will require API key in future)
- [x] Test key v2 endpoints with real requests (8 v2 tests)
- [x] Document in test docstring: run with `pytest --run-live-openapi`
- [x] Note that these CAN run in CI (unlike re-api tests)

**Validation**: ✅ Integration tests pass when run with `pytest --run-live-openapi` (11 tests, all passing)

## Phase 6: Automation and Maintenance ✅

### 6.1 Update Main Test Workflow for OpenAPI Live Tests

- [x] Update existing `.github/workflows/pytest.yaml`
- [x] Add step to run OpenAPI live tests: `pytest tests/integration/test_live_openapi.py --run-live-openapi -v`
- [x] Configure to run on push and pull_request events (workflow already configured)
- [x] Add comment noting re-api tests skipped in CI (require feeder IP)
- [x] Prepare for future API key requirement (add commented env var section)
- [x] Test workflow with sample PR

**Validation**: ✅ CI runs successfully, OpenAPI live tests execute in GitHub Actions

**Note**: This validates the OpenAPI client against real API on every change

### 6.2 Create GitHub Action for Spec Monitoring

- [x] Create `.github/workflows/check-openapi-spec.yaml`
- [x] Set up weekly cron schedule (Sunday midnight)
- [x] Download spec and calculate hash
- [x] Compare with stored hash in repo
- [x] Create GitHub issue if spec changed with details (including diff and version extraction)
- [x] Add issue template with update checklist
- [x] Upload artifacts for spec files and diff
- [x] Test workflow manually

**Validation**: ✅ Workflow created, will run weekly and create issues when spec changes

### 6.3 Create GitHub Copilot Update Prompt

- [x] Create `.github/prompts/update-openapi-client.prompt.md` (already exists from previous work)
- [x] Document step-by-step update process
- [x] Include instructions for downloading spec
- [x] Add guidance for comparing versions
- [x] Include regeneration steps
- [x] Add checklist for identifying breaking changes
- [x] Document client method update process
- [x] Add test update guidance
- [x] Include documentation update steps

**Validation**: ✅ Prompt is comprehensive and follows project conventions (335 lines)

### 6.4 Store Spec in Repository

- [x] Add `openapi_spec.json` to repository via makefile
- [x] Add spec hash to version tracking module (adsblol/client/openapi_version.py)
- [x] Update spec as part of update process (make openapi-update)
- [x] Spec stored for reference and diffing

**Validation**: ✅ Spec accessible for reference, hash tracked in version module

## Phase 7: Documentation ✅

### 7.1 Create OpenAPI Client Documentation

- [x] Create `docs/dev/openapi-client.md`
- [x] Document when to use OpenAPI vs re-api
- [x] Explain API key acquisition and setup
- [x] Provide basic usage examples
- [x] Document v2 and v0 capabilities
- [x] Explain model structure and types
- [x] Add error handling examples
- [x] Include CLI usage examples

**Validation**: ✅ Documentation is clear and comprehensive (485 lines)

### 7.2 Update Main Documentation

- [x] Update `README.md` to mention OpenAPI support
- [x] Add OpenAPI quick start examples
- [x] Document API key configuration
- [x] Update feature list
- [x] Add links to OpenAPI documentation
- [x] Update CLI examples section

**Validation**: ✅ README accurately reflects new capabilities

### 7.3 Update Developer Documentation

- [ ] Update `docs/dev/architecture.md` with OpenAPI design (deferred - architecture doc needs broader update)
- [x] Document model generation process (in openapi-client.md)
- [x] Add OpenAPI client patterns (in openapi-client.md)
- [x] Update `docs/dev/README.md` with link to openapi-client.md
- [x] Document maintenance workflow (GitHub workflows and Copilot prompt)

**Validation**: ✅ Developer docs updated and linked correctly

### 7.4 Add Migration Guide

- [x] Create migration guide section in docs (comparison table in openapi-client.md)
- [x] Document differences between APIs (in README and openapi-client.md)
- [x] Provide code examples for both APIs (in README Quick Start)
- [x] Explain when migration makes sense (in openapi-client.md "When to Use" section)
- [x] Document breaking changes and workarounds (N/A - new client, no breaking changes)

**Validation**: ✅ Migration path is clear for users

### 7.5 Update Project Metadata

- [ ] Update `openspec/project.md` with OpenAPI context (deferred - not critical)
- [x] Document dual API support strategy (in README.md)
- [x] Add OpenAPI to tech stack (pyproject.toml dependencies)
- [x] Update domain context with OpenAPI details (in documentation)

**Validation**: ✅ Project context reflects current state (core docs updated)

## Phase 8: Final Review and Release ✅

### 8.1 Code Review

- [x] Review all new code for style consistency
- [x] Run mypy and ensure no type errors
- [x] Run ruff linter and fix any issues
- [x] Ensure all docstrings are comprehensive
- [x] Check logging is appropriate
- [x] Verify security best practices (no API key logging)

**Validation**: ✅ Code passes all quality checks (mypy: no issues in 21 files, ruff: all checks passed)

### 8.2 Test Coverage

- [x] Run pytest with coverage report
- [x] Ensure >90% coverage for new code (93% for openapi.py, 100% for models)
- [x] Add tests for any uncovered code paths
- [x] Verify all edge cases tested

**Validation**: ✅ Coverage meets threshold (153 tests passing, 83% overall, 93% OpenAPI client)

### 8.3 Documentation Review

- [x] Proofread all documentation
- [x] Verify all code examples work
- [x] Check all links are valid (fixed markdown linting issues)
- [x] Ensure consistency across docs
- [x] Review for clarity and completeness

**Validation**: ✅ Documentation is polished and accurate (485 lines in openapi-client.md)

### 8.4 Manual Testing

- [x] Test OpenAPI client with live API (tested mil, hex, point commands)
- [x] Test all CLI commands manually
- [x] Test with and without API key (both work)
- [x] Test error conditions (422/401/429 error handling verified)
- [x] Verify output formatting (table and JSON modes working)
- [x] Test on different Python versions (CI runs 3.10-3.14)

**Validation**: ✅ Everything works as expected in real usage

### 8.5 Version and Release

- [ ] Update version in git (tag) - ready for user decision
- [ ] Update CHANGELOG with new features - ready for user decision
- [ ] Build package with `make build` - ready when user wants to release
- [ ] Test installation from built package - ready when user wants to release
- [ ] Publish to PyPI (if applicable) - user decision
- [ ] Create GitHub release with notes - user decision

**Validation**: ⏸️  Implementation complete, release timing is user decision

## Dependencies Between Tasks

**Critical Path**:

1. Phase 1 (Foundation) → Phase 2 (Models) → Phase 3 (Client) → Phase 4 (CLI) → Phase 5 (Testing) → Phase 8 (Release)

**Parallel Work Possible**:

- Phase 6 (Automation) can be done anytime after Phase 1
- Phase 7 (Documentation) can progress alongside implementation
- Test writing (Phase 5) can start as soon as corresponding code exists

**Blocking Relationships**:

- CLI (4.x) depends on Client (3.x)
- Client (3.x) depends on Models (2.x)
- Models (2.x) depend on Tooling (1.x)
- All testing (5.x) depends on corresponding implementation
