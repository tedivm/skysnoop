# Project Context

## Purpose

`adsblol` is a Python client library for interacting with the [adsb.lol](https://www.adsb.lol/) re-api (readsb HTTP API). The library provides a clean, typed, async-first interface for querying aircraft position and telemetry data from the adsb.lol network.

### Goals

- Provide a production-ready Python client for the adsb.lol re-api
- Support all query formats (circle, closest, box, all, find_hex, find_callsign, find_reg, find_type, etc.)
- Offer strongly typed data models for aircraft telemetry and metadata
- Enable async operations for high-performance applications
- Include comprehensive filtering and query building capabilities
- Provide both CLI and library interfaces for flexibility

## Tech Stack

### Core Technologies

- **Python 3.10+**: Minimum supported version
- **Pydantic 2.x**: Data validation and settings management with strong typing
- **Typer**: CLI framework for command-line interface
- **httpx** (planned): Async HTTP client for API requests

### Development Tools

- **pytest**: Testing framework with async support (pytest-asyncio)
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
- Provides free API access to feeders (contributors)
- Uses readsb as the underlying software
- API endpoint: `https://re-api.adsb.lol/`
- Access restricted by feeder IP addresses (requires VPN/proxy for other locations)
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

- **Feeder-Only**: API only accessible from feeder IP addresses
- **Rate Limiting**: Be respectful of API resources (implement reasonable timeouts and retries)
- **Data Freshness**: API cache frequency controlled by `--write-json-every` (typically 1 second for aircraft data)
- **No Authentication**: IP-based access control only

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

### Primary API

- **Service**: adsb.lol re-api (readsb HTTP API)
- **Endpoint**: `https://re-api.adsb.lol/`
- **Documentation**:
  - Usage: <https://www.adsb.lol/docs/feeders-only/re-api/>
  - Query Formats: <https://github.com/wiedehopf/readsb/blob/dev/README-json.md#--net-api-port-query-formats>
  - Data Model: <https://github.com/wiedehopf/readsb/blob/dev/README-json.md>
- **Example Query**: <https://re-api.adsb.lol/?circle=52,2,200>
- **Protocol**: HTTPS with URL query parameters
- **Response Format**: JSON

### Python Libraries

- **pydantic**: Data validation and settings (required)
- **pydantic-settings**: Configuration management (required)
- **typer**: CLI framework (required)
- **httpx**: Async HTTP client (to be added for API requests)

### Development Dependencies

- **Testing**: pytest, pytest-asyncio, pytest-cov, pytest-pretty
- **Type Checking**: mypy with pydantic plugin
- **Linting/Formatting**: ruff
- **Data/Development Tools**: dapperdata (data cleanup), glom (data access), ruamel.yaml
- **Build Tools**: build, setuptools, setuptools_scm, toml-sort

### Reference Implementation

The adsb.lol API is built on readsb, which is a Mode-S/ADS-B/TIS decoder. Understanding the readsb JSON output format is crucial for proper client implementation.
