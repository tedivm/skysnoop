# Project Context

## Purpose

`adsblol` is a Python client library for interacting with the [adsb.lol](https://www.adsb.lol/) API. The library provides two clients: a modern OpenAPI-based client for the public API, and a legacy RE-API client for feeder-specific endpoints. Both provide clean, typed, async-first interfaces for querying aircraft position and telemetry data from the adsb.lol network.

### Goals

- Provide production-ready Python clients for both adsb.lol APIs (OpenAPI and RE-API)
- Support all query formats (circle, closest, box, all, find_hex, find_callsign, find_reg, find_type, etc.)
- Offer strongly typed data models with auto-generated Pydantic models for OpenAPI
- Enable async operations for high-performance applications
- Include comprehensive filtering and query building capabilities
- Provide both CLI and library interfaces for flexibility
- Maintain dual API support with consistent patterns and interfaces

## Tech Stack

### Core Technologies

- **Python 3.10+**: Minimum supported version
- **Pydantic 2.x**: Data validation and settings management with strong typing
- **Typer**: CLI framework for command-line interface
- **httpx**: Async HTTP client for API requests
- **datamodel-code-generator**: Auto-generates Pydantic models from OpenAPI specifications

### Development Tools

- **pytest**: Testing framework with async support (pytest-asyncio)
- **respx**: HTTP mocking for testing async clients
- **mypy**: Static type checking
- **ruff**: Fast Python linter and formatter
- **setuptools_scm**: Version management from git tags

## Project Conventions

### Code Style

- **Python Version**: Minimum Python 3.10
- **Formatting**: Ruff with 120 character line length
- **Type Hints**: Mandatory for all functions, methods, and variables
- **Imports**: At top of file (unless circular import prevention needed)
- **Arguments**: Prefer keyword arguments over positional
- **Naming**:
  - Files: lowercase with underscores (e.g., `aircraft_data.py`)
  - Classes: PascalCase (e.g., `AircraftData`)
  - Functions/Variables: snake_case (e.g., `fetch_aircraft`)
  - Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)

### Architecture Patterns

- **Async-First**: Prefer async/await patterns for I/O operations
- **Pydantic Models**: Use Pydantic for data models and validation
- **Settings Management**: Centralized in `adsblol/conf/settings.py` using `pydantic-settings`
- **Separation of Concerns**:
  - API client code in `adsblol/client/` or `adsblol/api/`
  - Data models in `adsblol/models/`
  - CLI commands in `adsblol/cli.py`
  - Configuration in `adsblol/conf/`
- **Dependency Injection**: Settings and clients passed as parameters
- **Error Handling**: Specific exception classes, never suppress without logging

### Testing Strategy

- **Framework**: pytest with pytest-asyncio for async tests
- **Coverage**: pytest-cov with omissions for `_version.py`, `__init__.py`, and `tests/`
- **Structure**: Test suite mirrors main code structure
- **Fixtures**: Defined in `conftest.py` for reusability
- **Style**: Single test functions (no classes unless necessary)
- **Mocking**: Avoid mocking simple dataclasses/models; use real instances
- **Requirements**: New code must include corresponding tests

### Git Workflow

- **Branching**: Feature branches from main
- **Commits**: Clear, descriptive commit messages
- **Versioning**: Managed by setuptools_scm from git tags
- **OpenSpec**: Use for planning significant changes (see `openspec/AGENTS.md`)

### Logging

- Use `logging.getLogger(__name__)` in each module
- Never use `print()` for logging
- Log levels: DEBUG for verbose, INFO for normal, WARNING/ERROR as appropriate
- Log exceptions with `logger.exception()` to capture stack traces
- Never log sensitive data (API keys, personal information)

### Type Hints

- Use `|` union operator (e.g., `str | None`) instead of `Optional`
- Use typing library types: `Dict[str, str]`, `List[str]` instead of `dict`, `list`
- Avoid `Any` unless absolutely necessary
- Prefer Pydantic models or dataclasses over plain dictionaries

### Security

- Never hardcode credentials or API keys
- Use `SecretStr` or `SecretBytes` for sensitive configuration
- Validate all user input
- No custom cryptography
- Follow security best practices for HTTP requests

## Domain Context

### ADS-B Technology

ADS-B (Automatic Dependent Surveillance-Broadcast) is a surveillance technology where aircraft determine their position via satellite navigation and periodically broadcast it, enabling them to be tracked.

### ADSB.lol Network

- Community-driven ADS-B aggregation network
- Provides two API endpoints:
  - **OpenAPI** (`https://api.adsb.lol`): Public API with official OpenAPI specification, API keys required in future
  - **RE-API** (`https://re-api.adsb.lol`): Legacy feeder-only API, IP-restricted access for data contributors
- Uses readsb as the underlying software for RE-API
- OpenAPI v2 endpoints provide aircraft queries (hex, callsign, type, location, etc.)
- OpenAPI v0 endpoints provide utility functions (feeder info, routes)
- License: ODbL 1.0 (Open Database License)

### Aircraft Data Model

Aircraft objects contain extensive telemetry including:

- **Identity**: ICAO hex ID, registration, callsign, type
- **Position**: Latitude, longitude, altitude (barometric/geometric)
- **Velocity**: Ground speed, airspeed (IAS/TAS), Mach number
- **Navigation**: Track, heading (magnetic/true), vertical rate
- **Status**: Squawk code, emergency status, category
- **Quality Metrics**: NIC, NAC_P, NAC_V, SIL (navigation/position accuracy)
- **Source**: Type of data (adsb_icao, mlat, tisb, etc.)
- **Signal**: RSSI, message count, last seen timestamp

### Query Types

#### OpenAPI Client (Recommended)

1. **V2 Endpoints** (Aircraft Queries):
   - `get_by_hex`: By ICAO 24-bit identifier
   - `get_by_callsign`: By flight callsign
   - `get_by_registration`: By aircraft registration
   - `get_by_type`: By aircraft type code (e.g., A321, B738)
   - `get_by_squawk`: By squawk code
   - `get_by_point`: Aircraft within radius of coordinates
   - `get_closest`: Single closest aircraft within radius
   - `get_mil`: Military aircraft
   - `get_pia`: Privacy (PIA) flagged aircraft
   - `get_ladd`: LADD-protected aircraft

2. **V0 Endpoints** (Utility):
   - `get_me`: Feeder information and global stats
   - `get_routes`: Route information for aircraft
   - `get_airport`: Airport information by ICAO code (if available)

#### RE-API Client (Legacy)

1. **Spatial Queries**:
   - `circle`: Aircraft within radius of a point (includes distance and direction)
   - `closest`: Single closest aircraft within radius
   - `box`: Aircraft within a rectangular boundary

2. **Lookup Queries**:
   - `find_hex`: By ICAO 24-bit identifier
   - `find_callsign`: By flight callsign
   - `find_reg`: By aircraft registration
   - `find_type`: By aircraft type code (e.g., A321, B738)

3. **Bulk Queries**:
   - `all_with_pos`: All aircraft with recent positions
   - `all`: All aircraft with recent messages

4. **Filters**: Can combine with base queries
   - `filter_callsign_exact`, `filter_callsign_prefix`
   - `filter_squawk`, `filter_with_pos`, `filter_type`
   - `above_alt_baro`, `below_alt_baro`
   - `filter_mil`, `filter_pia`, `filter_ladd` (database flags)

### Response Format

```json
{
  "now": 1234567890.123,
  "resultCount": 42,
  "ptime": 0.049,
  "aircraft": [
    {
      "hex": "abc123",
      "flight": "UAL123",
      "lat": 37.7749,
      "lon": -122.4194,
      "alt_baro": 35000,
      ...
    }
  ]
}
```

## Important Constraints

### API Access

- **OpenAPI Client**:
  - Publicly accessible endpoint (`https://api.adsb.lol`)
  - API keys will be required in the future (currently optional)
  - Rate limiting may apply (watch for 429 responses)
  - Official OpenAPI 3.1.0 specification available
  - Spec version tracked in `adsblol/client/openapi_version.py`
  - Models auto-generated from spec using `datamodel-code-generator`

- **RE-API Client (Legacy)**:
  - Feeder-only API accessible from feeder IP addresses
  - IP-based access control only (no authentication)
  - Rate limiting: Be respectful of API resources
  - Data freshness controlled by `--write-json-every` (typically 1 second)
  - Requires VPN/proxy for non-feeder access

### Technical

- **Python Version**: 3.10 minimum (use modern syntax)
- **Production Ready**: No development-only stubs or logic in main package
- **Async Required**: I/O operations must be async
- **Type Safety**: All code must be fully typed
- **No FastAPI**: This is a client library, not a web service

### Data Quality

- Position data may be stale (check `seen_pos` field)
- Different data sources have different accuracy (check `type` field)
- Not all fields always present (optional/nullable types required)
- MLAT positions may have varying accuracy
- Aircraft may disappear from feed (5 minute timeout)

### License Compliance

- Data under ODbL 1.0 license
- Users must comply with license terms
- Attribution requirements for derived works

## External Dependencies

### Primary APIs

#### OpenAPI (Recommended)

- **Service**: adsb.lol OpenAPI
- **Endpoint**: `https://api.adsb.lol`
- **Documentation**:
  - API Docs: <https://api.adsb.lol/docs>
  - OpenAPI Spec: <https://api.adsb.lol/api/openapi.json>
  - Current Version: 0.0.2
- **Example Queries**:
  - <https://api.adsb.lol/api/v2/hex/4CA87C>
  - <https://api.adsb.lol/api/v2/mil>
- **Protocol**: HTTPS with RESTful paths
- **Response Format**: JSON (validated against OpenAPI spec)
- **Authentication**: API key support (optional now, required future)

#### RE-API (Legacy)

- **Service**: adsb.lol re-api (readsb HTTP API)
- **Endpoint**: `https://re-api.adsb.lol/`
- **Documentation**:
  - Usage: <https://www.adsb.lol/docs/feeders-only/re-api/>
  - Query Formats: <https://github.com/wiedehopf/readsb/blob/dev/README-json.md#--net-api-port-query-formats>
  - Data Model: <https://github.com/wiedehopf/readsb/blob/dev/README-json.md>
- **Example Query**: <https://re-api.adsb.lol/?circle=52,2,200>
- **Protocol**: HTTPS with URL query parameters
- **Response Format**: JSON
- **Authentication**: IP-based (feeder IPs only)

### Python Libraries

- **pydantic**: Data validation and settings (required)
- **pydantic-settings**: Configuration management (required)
- **typer**: CLI framework (required)
- **httpx**: Async HTTP client for API requests (required)
- **rich**: Terminal output formatting (required for CLI)

### Development Dependencies

- **Testing**: pytest, pytest-asyncio, pytest-cov, pytest-pretty, respx (HTTP mocking)
- **Type Checking**: mypy with pydantic plugin
- **Linting/Formatting**: ruff
- **Code Generation**: datamodel-code-generator (OpenAPI to Pydantic), openapi-python-client
- **Data/Development Tools**: dapperdata (data cleanup), glom (data access), ruamel.yaml
- **Build Tools**: build, setuptools, setuptools_scm, toml-sort

### Reference Implementation

The adsb.lol API is built on readsb, which is a Mode-S/ADS-B/TIS decoder. Understanding the readsb JSON output format is crucial for proper client implementation.
