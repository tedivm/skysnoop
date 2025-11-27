# OpenAPI Client

The `adsblol` package provides two API clients for accessing aircraft data:

- **OpenAPI Client** (recommended): Modern, auto-generated client based on the official OpenAPI specification
- **RE-API Client** (legacy): Original client using the feeder-based API

This document covers the OpenAPI client. For the legacy client, see [API Client](./api-client.md).

## Overview

The OpenAPI client (`OpenAPIClient`) provides access to aircraft data via the public `https://api.adsb.lol` API. It features:

- **Auto-generated models**: Pydantic models generated from the official OpenAPI spec ensure type safety and validation
- **Comprehensive coverage**: Supports both v2 (aircraft queries) and v0 (utility) endpoints
- **Type safety**: Full typing support for all methods and models
- **Error handling**: Detailed error messages with validation feedback
- **API key ready**: Optional API key support (required in the future)

## When to Use OpenAPI vs RE-API

### Use OpenAPI Client When

- You need general aircraft data queries (by hex, callsign, location, etc.)
- You want official, documented API endpoints
- You need type-safe, validated responses
- You're building new integrations (recommended approach)
- API keys will be available in the future

### Use RE-API Client When

- You have access to a feeder IP address
- You need feeder-specific functionality
- You're maintaining existing code using the RE-API

## Installation

The OpenAPI client is included with the main package:

```bash
pip install adsblol
```

For development (includes code generation tools):

```bash
pip install -e ".[dev]"
```

## API Key Setup (Future Requirement)

Currently, API keys are **not required** but the client is designed to support them when they become mandatory.

### Environment Variable

Set the `ADSBLOL_API_KEY` environment variable:

```bash
export ADSBLOL_API_KEY="your-api-key-here"
```

### Programmatic Configuration

Pass the API key directly to the client:

```python
from adsblol.client import OpenAPIClient

async with OpenAPIClient(api_key="your-api-key-here") as client:
    # Use client
    pass
```

## Basic Usage

### Async Context Manager (Recommended)

```python
from adsblol.client import OpenAPIClient

async def main():
    async with OpenAPIClient() as client:
        # Query aircraft by ICAO hex
        response = await client.v2.get_by_hex(icao_hex="4CA87C")

        # Access aircraft data
        for aircraft in response.ac:
            print(f"{aircraft.hex}: {aircraft.flight} at {aircraft.alt_baro}ft")

# Run async code
import asyncio
asyncio.run(main())
```

### Manual Lifecycle Management

```python
from adsblol.client import OpenAPIClient

async def main():
    client = OpenAPIClient()

    try:
        response = await client.v2.get_by_hex(icao_hex="4CA87C")
        print(response)
    finally:
        await client.close()

import asyncio
asyncio.run(main())
```

## V2 Methods (Aircraft Queries)

### Get Aircraft by ICAO Hex

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_by_hex(icao_hex="4CA87C")
```

### Get Aircraft by Callsign

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_by_callsign(callsign="UAL123")
```

### Get Aircraft by Registration

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_by_registration(registration="N12345")
```

### Get Aircraft by Type

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_by_type(aircraft_type="B77W")
```

### Get Aircraft by Squawk Code

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_by_squawk(squawk="7700")  # Emergency
```

### Get Military Aircraft

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_mil()
```

### Get Privacy (PIA) Flagged Aircraft

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_pia()
```

### Get LADD-Protected Aircraft

```python
async with OpenAPIClient() as client:
    response = await client.v2.get_ladd()
```

### Get Aircraft Near a Point

```python
async with OpenAPIClient() as client:
    # Within 50nm of San Francisco
    response = await client.v2.get_by_point(
        lat=37.7749,
        lon=-122.4194,
        radius=50
    )
```

### Get Closest Aircraft

```python
async with OpenAPIClient() as client:
    # Find aircraft closest to coordinates within 100nm
    response = await client.v2.get_closest(
        lat=37.7749,
        lon=-122.4194,
        radius=100
    )
```

## V0 Methods (Utility)

### Get My Feeder Info

```python
async with OpenAPIClient() as client:
    response = await client.v0.get_me()
    print(response)  # Dict with feeder information
```

### Get Routes for Aircraft

```python
async with OpenAPIClient() as client:
    # Get routes for multiple aircraft
    planes = ["4CA87C", "A12345"]
    response = await client.v0.get_routes(planes=planes)
    print(response)  # Dict with route information
```

## Response Models

### V2ResponseModel

All v2 methods return a `V2ResponseModel`:

```python
from adsblol.models.openapi import V2ResponseModel

response: V2ResponseModel = await client.v2.get_by_hex("4CA87C")

# Response attributes
response.ac          # List[V2ResponseAcItem]: Aircraft data
response.ctime       # float: Current timestamp
response.msg         # str: Message (e.g., "No error")
response.now         # float: Current time
response.ptime       # int: Processing time
response.total       # int: Total aircraft count
```

### V2ResponseAcItem

Each aircraft in the response is a `V2ResponseAcItem`:

```python
for aircraft in response.ac:
    # Common fields
    aircraft.hex           # str: ICAO hex code
    aircraft.flight        # Optional[str]: Callsign
    aircraft.alt_baro      # Optional[int]: Barometric altitude (feet)
    aircraft.gs            # Optional[float]: Ground speed (knots)
    aircraft.track         # Optional[float]: Track/heading (degrees)
    aircraft.lat           # Optional[float]: Latitude
    aircraft.lon           # Optional[float]: Longitude

    # Additional fields
    aircraft.r             # Optional[str]: Registration
    aircraft.t             # Optional[str]: Aircraft type
    aircraft.squawk        # Optional[str]: Squawk code
    aircraft.emergency     # Optional[str]: Emergency status
    aircraft.category      # Optional[str]: Aircraft category
    aircraft.nav_altitude_mcp  # Optional[int]: MCP altitude
    aircraft.nav_heading   # Optional[float]: Nav heading

    # Many more fields available - see generated models
```

## Error Handling

The OpenAPI client raises specific exceptions for different error conditions:

```python
from adsblol.exceptions import (
    OpenAPIValidationError,
    AuthenticationError,
    RateLimitError,
    APIError
)

async with OpenAPIClient() as client:
    try:
        response = await client.v2.get_by_hex(icao_hex="INVALID")
    except OpenAPIValidationError as e:
        # 422 validation error with details
        print(f"Validation error: {e}")
        print(f"Details: {e.details}")
    except AuthenticationError as e:
        # 401 authentication error
        print(f"Authentication failed: {e}")
    except RateLimitError as e:
        # 429 rate limit error
        print(f"Rate limited. Retry after: {e.retry_after}")
    except APIError as e:
        # Generic API error
        print(f"API error: {e}")
```

## CLI Usage

The OpenAPI client is also accessible via CLI commands:

### V2 Commands

```bash
# Get aircraft by hex
adsblol openapi v2 hex 4CA87C

# Get military aircraft
adsblol openapi v2 mil

# Get aircraft near a point (note: use -- before negative longitude)
adsblol openapi v2 point 37.7749 -- -122.4194 50

# Get closest aircraft
adsblol openapi v2 closest 37.7749 -- -122.4194 100

# Output as JSON
adsblol openapi v2 hex 4CA87C --json

# Use API key
adsblol openapi v2 hex 4CA87C --api-key YOUR_KEY
```

### V0 Commands

```bash
# Get feeder info
adsblol openapi v0 me

# Output as JSON
adsblol openapi v0 me --json
```

## Advanced Features

### Logging

The client logs important events including:

- API version on initialization
- HTTP request details (URL, method)
- Error responses

Enable debug logging to see all HTTP activity:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("adsblol.client.openapi")
logger.setLevel(logging.DEBUG)
```

### Custom HTTP Client Configuration

The OpenAPI client uses `BaseHTTPClient` which is based on `httpx.AsyncClient`. You can customize the underlying HTTP client behavior by modifying the client after initialization:

```python
async with OpenAPIClient() as client:
    # Access underlying HTTP client
    client.client.timeout = httpx.Timeout(30.0)  # Set custom timeout
```

### Response Validation

All responses are validated against the Pydantic models. If the API returns unexpected data, a validation error will be raised:

```python
try:
    response = await client.v2.get_by_hex("4CA87C")
except Exception as e:
    print(f"Unexpected response format: {e}")
```

## Model Generation

The OpenAPI models are auto-generated from the official API specification. To regenerate models after spec updates:

```bash
# Download latest spec and regenerate models
make openapi-update
```

This will:

1. Download the latest OpenAPI spec from `https://api.adsb.lol/api/openapi.json`
2. Generate Pydantic models in `adsblol/models/openapi/generated.py`
3. Update version tracking in `adsblol/client/openapi_version.py`

## Version Information

Check the current OpenAPI spec version:

```python
from adsblol.client.openapi_version import (
    OPENAPI_VERSION,
    SPEC_HASH,
    SPEC_UPDATED
)

print(f"OpenAPI Version: {OPENAPI_VERSION}")
print(f"Spec Hash: {SPEC_HASH}")
print(f"Last Updated: {SPEC_UPDATED}")
```

## Testing

### Unit Tests

Run OpenAPI client tests:

```bash
pytest tests/models/test_openapi_models.py -v
pytest tests/client/test_openapi.py -v
```

### Integration Tests

Run tests against the live API:

```bash
pytest tests/integration/test_live_openapi.py --run-live-openapi -v
```

**Note**: These tests make real API calls and are automatically run in CI.

## Comparison with RE-API Client

| Feature | OpenAPI Client | RE-API Client |
|---------|---------------|---------------|
| **Base URL** | `https://api.adsb.lol` | Feeder-specific |
| **Authentication** | API key (future) | None |
| **Documentation** | Official OpenAPI spec | Informal |
| **Type Safety** | Full Pydantic models | Basic dataclasses |
| **Endpoint Coverage** | V2 + V0 endpoints | RE-API endpoints |
| **CI Testing** | ✅ Yes | ❌ No (requires feeder) |
| **Recommended** | ✅ For new code | Legacy support |

## Troubleshooting

### Import Errors

If you see import errors for OpenAPI models:

```bash
# Ensure dev dependencies are installed
pip install -e ".[dev]"

# Regenerate models
make openapi-update
```

### Validation Errors

If you receive unexpected validation errors, the API spec may have changed:

```bash
# Update to latest models
make openapi-update

# Check current spec version
python -c "from adsblol.client.openapi_version import OPENAPI_VERSION; print(OPENAPI_VERSION)"
```

### Rate Limiting

If you encounter rate limiting (429 errors):

- Wait for the duration specified in `retry_after`
- Consider caching responses
- Request an API key (when available)

### Connection Errors

For connection timeouts or network errors:

- Check your internet connection
- Verify the API is accessible: `curl https://api.adsb.lol/api/v2/hex/4CA87C`
- Increase timeout if needed

## Resources

- **OpenAPI Spec**: <https://api.adsb.lol/api/openapi.json>
- **API Documentation**: <https://api.adsb.lol/docs>
- **Model Generation**: [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)
- **HTTP Client**: [httpx](https://www.python-httpx.org/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

## See Also

- [API Client (RE-API)](./api-client.md) - Legacy feeder-based client
- [Architecture](./architecture.md) - Overall project architecture
- [CLI Commands](./cli.md) - Command-line interface documentation
- [Testing](./testing.md) - Testing guidelines
