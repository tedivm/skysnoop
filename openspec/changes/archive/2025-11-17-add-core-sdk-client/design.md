# Design: Add Core SDK Client

## Overview

This design document outlines the architecture for implementing the core SDK client for the adsblol library. The implementation follows an async-first, type-safe approach organized into four main components: data models, API client, query filtering, and CLI commands.

## Architecture

### Component Structure

```
adsblol/
├── models/
│   ├── __init__.py
│   ├── aircraft.py         # Aircraft data model
│   └── response.py         # API response models
├── client/
│   ├── __init__.py
│   ├── base.py             # Base HTTP client
│   └── api.py              # High-level API client
├── query/
│   ├── __init__.py
│   ├── builder.py          # Query parameter builder
│   └── filters.py          # Filter types and builders
├── exceptions.py           # Custom exceptions
└── cli.py                  # CLI commands (extend existing)
```

### Data Flow

1. **User Request** → CLI command or library call
2. **Query Building** → QueryBuilder constructs URL parameters
3. **HTTP Request** → HTTPClient makes async request to API
4. **Response Parsing** → JSON parsed into Pydantic models
5. **Result Return** → Typed aircraft data returned to user

## Component Details

### 1. Data Models (models/)

#### Aircraft Model

Represents a single aircraft with all telemetry fields. Key design decisions:

- **All fields optional**: API doesn't guarantee all fields present
- **Type conversions**: Handle numeric strings, timestamps, etc.
- **Computed properties**: Add convenience properties (e.g., `has_position`)
- **Validation**: Use Pydantic validators for range checks

#### Response Model

Wraps API responses with metadata:

- `now`: Server timestamp
- `resultCount`: Number of aircraft
- `ptime`: Processing time
- `aircraft`: List of aircraft objects

#### Design Rationale

- Pydantic provides automatic validation and serialization
- Optional fields prevent crashes on missing data
- Type hints enable IDE autocomplete and type checking
- Forward compatibility with `extra="allow"`

### 2. API Client (client/)

#### BaseHTTPClient

Low-level HTTP client wrapping httpx:

```python
class BaseHTTPClient:
    def __init__(
        self,
        base_url: str = "https://re-api.adsb.lol/",
        timeout: float = 30.0,
    ):
        self._client = httpx.AsyncClient(...)

    async def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Make request, handle errors, return JSON
```

**Features:**

- Async context manager support
- Connection pooling via httpx
- Timeout configuration
- Error handling with custom exceptions

#### ReAPIClient

High-level client with query methods:

```python
class ReAPIClient:
    async def circle(
        self,
        lat: float,
        lon: float,
        radius: int,
        filters: QueryFilters | None = None,
    ) -> APIResponse:
        # Build query, make request, parse response
```

**Methods:**

- `circle()`, `closest()`, `box()`
- `find_hex()`, `find_callsign()`, `find_reg()`, `find_type()`
- `all_with_pos()`, `all()`
- Common `_execute()` method for DRY principle

#### Design Rationale

- Separation: BaseHTTPClient handles HTTP, ReAPIClient handles domain logic
- Async/await for non-blocking I/O
- Connection reuse via httpx.AsyncClient
- Type hints for all parameters and return values

### 3. Query Filtering (query/)

#### QueryBuilder

Constructs URL query strings from query objects:

```python
class QueryBuilder:
    def build_circle(
        self,
        lat: float,
        lon: float,
        radius: int,
        filters: QueryFilters | None = None,
    ) -> str:
        # Return query string like "circle=lat,lon,radius&filter1=value1"
        # NOTE: Must return string, not dict - httpx URL-encodes commas which breaks API
```

#### QueryFilters

Dataclass or Pydantic model for filter options:

```python
@dataclass
class QueryFilters:
    callsign_exact: str | None = None
    callsign_prefix: str | None = None
    squawk: str | None = None
    type_code: str | None = None
    above_alt_baro: int | None = None
    below_alt_baro: int | None = None
    mil: bool | None = None
    pia: bool | None = None
    ladd: bool | None = None
```

#### Design Rationale

- Centralized query building logic
- Type-safe filter definitions
- Easy to extend with new filter types
- Validation of filter combinations

#### URL Encoding Constraint

**CRITICAL**: The adsb.lol API uses comma-separated values in query parameters (e.g., `circle=52.5,13.4,100`).

**Problem**: httpx's `params` parameter automatically URL-encodes all special characters, including commas. This converts `circle=52.5,13.4,100` to `circle=52.5%2C13.4%2C100`, which the API rejects with a 400 error.

**Solution**:

- QueryBuilder returns pre-formatted query strings (e.g., `"circle=52.5,13.4,100&filter=value"`)
- BaseHTTPClient constructs URLs manually: `f"{base_url}?{query_string}"`
- Do NOT use httpx's `params` parameter for adsb.lol queries
- Only URL-encode filter values that might contain special characters, not the structural commas

**Example**:

```python
# WRONG - httpx will encode commas
await client.get(params={"circle": "52.5,13.4,100"})  # → circle=52.5%2C13.4%2C100 ❌

# CORRECT - manual string construction
query = "circle=52.5,13.4,100"
await client.get(f"{base_url}?{query}")  # → circle=52.5,13.4,100 ✓
```

### 4. CLI Commands (cli.py)

Extend existing Typer app with aircraft query commands:

```python
@app.command()
@syncify
async def circle(
    lat: float,
    lon: float,
    radius: int,
    callsign: str | None = None,
    type_code: str | None = None,
):
    # Create client, execute query, display results
```

**Commands:**

- `adsblol circle LAT LON RADIUS` - Search within radius
- `adsblol closest LAT LON RADIUS` - Find closest aircraft
- `adsblol find-hex HEX` - Lookup by ICAO hex
- `adsblol find-callsign CALLSIGN` - Lookup by callsign
- `adsblol all` - Get all aircraft with positions

**Output Format:**

- Default: Human-readable table
- JSON option: `--json` flag for machine parsing

#### Design Rationale

- Reuse existing syncify decorator for async support
- Common filters as CLI options
- JSON output for scripting use cases
- Progress indicators for long queries

## Error Handling

### Exception Hierarchy

```python
class ADSBLolError(Exception):
    """Base exception"""

class APIError(ADSBLolError):
    """API request failed"""

class ValidationError(ADSBLolError):
    """Invalid parameters"""

class TimeoutError(ADSBLolError):
    """Request timed out"""
```

### Error Scenarios

1. **Network errors**: Wrap httpx exceptions in APIError
2. **Invalid responses**: Raise APIError with response details
3. **Timeout**: Raise TimeoutError with context
4. **Validation**: Raise ValidationError for bad parameters

## Configuration

Settings to add to `conf/settings.py`:

```python
class Settings(BaseSettings):
    # Existing fields...

    # API settings
    adsb_api_base_url: str = "https://re-api.adsb.lol/"
    adsb_api_timeout: float = 30.0

    # CLI settings
    cli_output_format: Literal["table", "json"] = "table"
```

## Testing Strategy

### Critical Requirement: Real API Data for Mocks

**ALL mock data MUST come from real API responses.** This is non-negotiable because:

1. The adsb.lol API is only accessible from feeder IP addresses
2. Tests need to run in CI/CD environments (GitHub Actions) without API access
3. Real API data ensures tests cover actual data structures, edge cases, and variations
4. Synthetic mock data may miss important fields, types, or scenarios

**Process for creating mock data:**

1. Developer must have API access (feeder IP or VPN) during test development
2. Execute each query type against the live API and capture responses
3. Save responses as JSON fixtures in `tests/fixtures/api_responses/`
4. Organize by query type: `circle_response.json`, `find_hex_response.json`, etc.
5. Include variations: empty results, single aircraft, multiple aircraft, edge cases
6. Document capture date and query parameters in fixture metadata

**Fixture organization:**

```
tests/
├── fixtures/
│   ├── api_responses/
│   │   ├── circle_multiple_aircraft.json
│   │   ├── circle_single_aircraft.json
│   │   ├── circle_zero_results.json
│   │   ├── find_hex_success.json
│   │   ├── find_callsign_multiple.json
│   │   ├── all_with_pos_sample.json
│   │   └── error_responses.json
│   └── README.md  # Documents fixture creation process
└── conftest.py
```

### Unit Tests

- **Models**: Test validation, defaults, optional fields using real API response fixtures
- **QueryBuilder**: Test parameter construction for all query types
- **Filters**: Test filter combination logic

### Integration Tests

- **Client**: Mock httpx responses using captured real API data
- **End-to-end**: Use recorded API responses for realistic tests
- **CLI**: Test command execution with mocked client using real response fixtures

### Test Fixtures (conftest.py)

```python
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "api_responses"

@pytest.fixture
def sample_aircraft_data() -> Dict[str, Any]:
    """Return real API response data captured from live API"""
    with open(FIXTURES_DIR / "circle_multiple_aircraft.json") as f:
        return json.load(f)

@pytest.fixture
def empty_response_data() -> Dict[str, Any]:
    """Return real API response with zero results"""
    with open(FIXTURES_DIR / "circle_zero_results.json") as f:
        return json.load(f)

@pytest.fixture
def mock_http_client(sample_aircraft_data) -> AsyncMock:
    """Return mocked HTTP client with real API response data"""
    client = AsyncMock()
    client.get.return_value = sample_aircraft_data
    return client

@pytest.fixture
async def api_client() -> ReAPIClient:
    """Return configured API client"""
```

## Performance Considerations

1. **Connection Pooling**: httpx.AsyncClient reuses connections
2. **Async Operations**: Non-blocking I/O for concurrent requests
3. **Minimal Processing**: Parse JSON directly into Pydantic models
4. **No Caching**: Let users implement caching as needed

## Security Considerations

1. **No Secrets**: IP-based authentication only
2. **Input Validation**: Validate lat/lon ranges, radius limits
3. **URL Construction**: Use httpx parameter handling (no manual URL building)
4. **Error Messages**: Don't leak sensitive information in exceptions

## Future Extensibility

Design supports future enhancements:

1. **Caching Layer**: Add cache between client and HTTP layer
2. **Batch Queries**: Support multiple queries in parallel
3. **WebSocket Support**: Add separate streaming client
4. **Local Database**: Add persistence layer for historical data
5. **Advanced Filters**: Complex filter combinations with AND/OR logic

## Dependencies

### New Dependencies

- `httpx` - Async HTTP client (required)

### Version Constraints

- `httpx>=0.25.0` - For async support and modern API

## Migration Path

N/A - This is the initial implementation, no migration needed.

## Rollout Plan

1. **Phase 1**: Merge data models (low risk)
2. **Phase 2**: Merge base HTTP client (testable independently)
3. **Phase 3**: Merge API client with basic queries
4. **Phase 4**: Add filtering and remaining query types
5. **Phase 5**: Add CLI commands
6. **Phase 6**: Update documentation and examples

Each phase includes tests and can be deployed independently.
