# Architecture Documentation

This document describes the architecture and design of the adsblol SDK.

## Overview

The adsblol SDK is organized into several layers, each with specific responsibilities:

```mermaid
flowchart TD
    CLI["CLI Layer (cli.py)<br/>• Typer commands<br/>• Output formatting (cli_formatters.py)<br/>• Error handling decorators"]
    API["High-Level API (client/api.py)<br/>• ADSBLolClient<br/>• Convenience methods for queries<br/>• Async context manager"]
    HTTP["HTTP Client (client/base.py)<br/>• BaseHTTPClient<br/>• HTTP request handling<br/>• Error translation"]
    Query["Query Building (query/)<br/>• QueryBuilder (builder.py)<br/>• QueryFilters (filters.py)<br/>• URL query string construction"]
    Models["Data Models (models/)<br/>• Aircraft (aircraft.py)<br/>• APIResponse (response.py)<br/>• Pydantic validation"]

    CLI --> API
    API --> HTTP
    HTTP --> Query
    Query --> Models
```

## Component Descriptions

### CLI Layer

**Location**: `adsblol/cli.py`, `adsblol/cli_formatters.py`

**Purpose**: Provides command-line interface for end users.

**Key Components**:

- **Commands**: Each API query type has a corresponding Typer command
- **Decorators**:
  - `@syncify` - Converts async functions to sync for Typer
  - `@handle_errors` - Catches exceptions and displays user-friendly messages
- **Formatters**: Rich table output, JSON output, and compact output

**Design Decisions**:

- Used Rich library for beautiful terminal tables
- All commands support `--json` flag for machine-readable output
- Filter options are consistent across all applicable commands
- Error messages include helpful suggestions

### High-Level API Client

**Location**: `adsblol/client/api.py`

**Purpose**: Provides a developer-friendly interface to the adsb.lol API.

**Key Components**:

- **ADSBLolClient**: Main client class with methods for each query type
- **Async Context Manager**: Manages HTTP client lifecycle
- **Method Organization**:
  - Geographic queries: `circle()`, `closest()`, `box()`
  - Identifier queries: `find_hex()`, `find_callsign()`, `find_reg()`, `find_type()`
  - Bulk queries: `all()`, `all_with_pos()`

**Design Decisions**:

- Async-first design using httpx
- Context manager pattern ensures proper resource cleanup
- Delegates query string construction to QueryBuilder
- Delegates HTTP operations to BaseHTTPClient
- Returns typed `APIResponse` objects

### HTTP Client

**Location**: `adsblol/client/base.py`

**Purpose**: Handles low-level HTTP communication with the API.

**Key Components**:

- **BaseHTTPClient**: Wraps httpx.AsyncClient
- **Error Translation**: Converts httpx exceptions to custom exceptions
- **URL Construction**: Builds full URLs from query strings

**Design Decisions**:

- Manual URL construction to preserve commas (critical for API)
- httpx chosen for async support and modern API
- Converts JSON responses to Pydantic models
- Timeout and base URL are configurable

**Critical Implementation Detail**:
The API requires commas in query parameters (e.g., `circle=37.7,-122.4,50`). Using httpx's `params` dict would URL-encode commas to `%2C`, breaking the API. Therefore, we:

1. Build query strings manually in QueryBuilder
2. Concatenate with base URL using f-strings
3. Never use httpx's `params` parameter

### Query Building

**Location**: `adsblol/query/builder.py`, `adsblol/query/filters.py`

**Purpose**: Constructs URL query strings for API requests.

**Key Components**:

- **QueryBuilder**: Static methods that build query strings
- **QueryFilters**: Pydantic model for filter parameters with validation

**Design Decisions**:

- Builder returns strings, not dicts, to avoid URL encoding
- Filters use Pydantic for validation (e.g., altitude range checks)
- Mutual exclusion enforced for conflicting filters
- Boolean filters use "true"/"false" strings (not "1"/"0")

**Example Flow**:

```python
# 1. Create filters
filters = QueryFilters(above_alt_baro=30000, type_code="A321")

# 2. Build query string
query = QueryBuilder.build_circle(
    lat=37.7749,
    lon=-122.4194,
    radius=200,
    filters=filters
)
# Result: "circle=37.7749,-122.4194,200&filter_above_alt_baro=30000&filter_type=A321"

# 3. Send request
response = await http_client.get(query)
```

### Data Models

**Location**: `adsblol/models/aircraft.py`, `adsblol/models/response.py`

**Purpose**: Type-safe data structures for API responses.

**Key Components**:

- **Aircraft**: Individual aircraft telemetry (60+ fields)
- **APIResponse**: Response wrapper with metadata and aircraft list

**Design Decisions**:

- Pydantic models for validation and serialization
- Forward compatibility with `extra="allow"`
- Altitude can be int or "ground" literal (special handling)
- Properties for computed values (e.g., `has_position`)
- Rich string representations for debugging

### Exception Hierarchy

**Location**: `adsblol/exceptions.py`

**Purpose**: Custom exceptions for clear error handling.

**Hierarchy**:

```mermaid
classDiagram
    ADSBLolError <|-- APIError
    ADSBLolError <|-- ValidationError
    ADSBLolError <|-- TimeoutError

    class ADSBLolError {
        <<base exception>>
    }
    class APIError {
        HTTP/API errors
    }
    class ValidationError {
        Invalid parameters
    }
    class TimeoutError {
        Request timeouts
    }
```

**Design Decisions**:

- All custom exceptions inherit from `ADSBLolError`
- Allows catching all library errors with single except block
- Specific exceptions for different error types
- httpx exceptions translated to custom exceptions

## Data Flow

### Typical Query Flow

1. **User initiates query** (CLI or library)

   ```python
   # CLI: adsblol circle -- 37.7749 -122.4194 50
   # Library: await client.circle(lat=37.7749, lon=-122.4194, radius=50)
   ```

2. **High-level client method called**
   - Validates parameters (implicit via type hints)
   - Creates QueryBuilder call

3. **Query string constructed**
   - QueryBuilder.build_circle() returns string
   - QueryFilters.to_query_string() appends filters

4. **HTTP request sent**
   - BaseHTTPClient.get() concatenates URL
   - httpx.AsyncClient executes request
   - Response JSON parsed

5. **Response validated**
   - Pydantic validates against Aircraft model
   - APIResponse wraps aircraft list

6. **Result returned**
   - CLI formats and displays
   - Library returns APIResponse

### Error Handling Flow

```mermaid
flowchart TD
    A["HTTP Error (httpx)"] --> B["BaseHTTPClient catches"]
    B --> C["Translates to APIError/TimeoutError"]
    C --> D["ADSBLolClient propagates"]
    D --> E{"Entry Point"}
    E -->|CLI| F["handle_errors decorator catches"]
    E -->|Library| G["User catches"]
    F --> H["User-friendly message displayed"]
    G --> I["Exception raised"]
```

## Testing Strategy

See [testing.md](testing.md) for comprehensive testing documentation.

## Configuration

**Location**: `adsblol/settings.py`, `adsblol/conf/settings.py`

**Configurable Settings**:

- `adsb_api_base_url`: API base URL (default: <https://re-api.adsb.lol/>)
- `adsb_api_timeout`: Request timeout in seconds (default: 30.0)
- `cli_output_format`: Default CLI output format (default: "table")

**Configuration Methods**:

1. Environment variables (e.g., `ADSB_API_BASE_URL`)
2. Direct settings object modification
3. Client constructor parameters (overrides settings)

## Design Patterns

### Async Context Manager

Used in:

- `ADSBLolClient`
- `BaseHTTPClient`

Benefits:

- Automatic resource cleanup
- Clear lifecycle management
- Pythonic API

### Builder Pattern

Used in:

- `QueryBuilder`

Benefits:

- Separates query construction from execution
- Centralized query string logic
- Easy to test independently

### Decorator Pattern

Used in:

- `@syncify` for async-to-sync conversion
- `@handle_errors` for CLI error handling

Benefits:

- Reusable functionality
- Clean separation of concerns
- DRY principle

### Pydantic Models

Used throughout for data validation.

Benefits:

- Runtime validation
- Type safety
- Automatic serialization/deserialization
- Forward compatibility

## Adding New Features

### Adding a New Query Type

1. **Add method to QueryBuilder**:

   ```python
   @staticmethod
   def build_new_query(param1: str, param2: int, filters: QueryFilters | None = None) -> str:
       query = f"new_query={param1},{param2}"
       if filters:
           filter_string = filters.to_query_string()
           if filter_string:
               query = f"{query}&{filter_string}"
       return query
   ```

2. **Add method to ADSBLolClient**:

   ```python
   async def new_query(
       self,
       param1: str,
       param2: int,
       filters: QueryFilters | None = None,
   ) -> APIResponse:
       """Description of new query.

       Args:
           param1: Description
           param2: Description
           filters: Optional filter criteria

       Returns:
           APIResponse with matching aircraft
       """
       self._ensure_client()
       query = QueryBuilder.build_new_query(param1, param2, filters)
       return await self._http_client.get(query)
   ```

3. **Add CLI command**:

   ```python
   @app.command(help="Description of new query")
   @handle_errors
   @syncify
   async def new_query(
       param1: str = typer.Argument(..., help="Description"),
       param2: int = typer.Argument(..., help="Description"),
       # ... filter options ...
       json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
   ):
       filters = _build_filters(...)
       async with ADSBLolClient() as client:
           response = await client.new_query(param1, param2, filters)
       format_output(response, format_type="json" if json_output else settings.cli_output_format)
   ```

4. **Add tests** (see testing.md)

### Adding a New Filter

1. **Add field to QueryFilters**:

   ```python
   class QueryFilters(BaseModel):
       # ... existing fields ...
       new_filter: str | None = Field(None, description="Description")
   ```

2. **Add to query params conversion**:

   ```python
   def to_query_params(self) -> dict[str, str]:
       params: dict[str, str] = {}
       # ... existing conversions ...
       if self.new_filter is not None:
           params["filter_new"] = self.new_filter
       return params
   ```

3. **Add CLI option to applicable commands**:

   ```python
   new_filter: Optional[str] = typer.Option(None, "--new-filter", help="Description")
   ```

4. **Update _build_filters helper**:

   ```python
   filter_params = {
       # ... existing params ...
       "new_filter": new_filter,
   }
   ```

## Performance Considerations

- **Async/Await**: All I/O operations are async for high concurrency
- **Connection Pooling**: httpx AsyncClient pools connections automatically
- **No Caching**: API data changes rapidly, so no caching is implemented
- **Lazy Evaluation**: Models use Pydantic's lazy validation where possible

## Security Considerations

- **No Sensitive Data**: API requires no authentication
- **Input Validation**: Pydantic validates all input parameters
- **Safe Defaults**: Reasonable timeouts prevent hanging
- **No SQL Injection**: Not applicable (REST API, not database)
- **URL Encoding**: Manual construction avoids encoding issues
