# Advanced Usage

This guide covers advanced features and use cases for SkySnoop, including direct backend access, custom configuration, and integration patterns.

## Low-Level Clients

While the `SkySnoop` unified client is recommended for most use cases, you can access backend APIs directly when needed.

### When to Use Low-Level Clients

**Use SkySnoop client (recommended)**:

- ✅ Standard aircraft queries
- ✅ Want automatic backend selection
- ✅ Need normalized responses
- ✅ Building new applications

**Use low-level clients**:

- Need backend-specific features
- Working with raw API responses
- Performance optimization for specific backends
- Debugging or testing backend behavior
- Maintaining existing code

### ReAPIClient (RE-API Backend)

Direct access to the feeder-only RE-API:

```python
from skysnoop.client import ReAPIClient

async with ReAPIClient() as client:
    # Returns APIResponse (not SkyData)
    response = await client.find_hex("4CA87C")

    print(f"Results: {response.resultCount}")
    print(f"Processing time: {response.ptime}ms")

    for aircraft in response.aircraft:
        print(f"{aircraft.hex}: {aircraft.flight}")
```

**Key differences from SkySnoop**:

- Returns `APIResponse` instead of `SkyData`
- Direct query builder access
- No backend abstraction
- Feeder-only access required

**See**: [RE-API Client Developer Documentation](./dev/reapi-client.md)

### OpenAPIClient (OpenAPI Backend)

Direct access to the public OpenAPI:

```python
from skysnoop.client import OpenAPIClient

async with OpenAPIClient() as client:
    # Returns V2ResponseModel (not SkyData)
    response = await client.v2.get_by_hex("4CA87C")

    print(f"Total results: {response.total}")
    print(f"Timestamp: {response.now}")

    for aircraft in response.ac:  # Note: 'ac' not 'aircraft'
        print(f"{aircraft.hex}: {aircraft.flight}")
```

**Key differences from SkySnoop**:

- Returns `V2ResponseModel` instead of `SkyData`
- Separate v2/v0 namespaces
- Direct API endpoint access
- Public access (no feeder required)

**See**: [OpenAPI Client Developer Documentation](./dev/openapi-client.md)

## Backend Selection Strategies

### Automatic Selection

The default `backend="auto"` selects based on configuration:

```python
async with SkySnoop() as client:
    # Auto-selection logic:
    # 1. If api_key provided → OpenAPI
    # 2. Otherwise → RE-API (preferred)
    result = await client.get_by_hex("4CA87C")
```

### Explicit Backend Selection

Force a specific backend:

```python
# Always use RE-API
async with SkySnoop(backend="reapi") as client:
    result = await client.get_all_with_pos()

# Always use OpenAPI
async with SkySnoop(backend="openapi") as client:
    result = await client.get_by_hex("4CA87C")
```

### Runtime Backend Detection

Check which backend is being used:

```python
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")

    if result.backend == "reapi":
        print("Using RE-API backend")
        # Can use filters, bulk queries, etc.
    elif result.backend == "openapi":
        print("Using OpenAPI backend")
        # Some features may be simulated
```

### Conditional Logic Based on Backend

```python
async with SkySnoop() as client:
    if client.backend_type == "reapi":
        # Use RE-API specific features
        filters = QueryFilters(military=True)
        result = await client.get_all_with_pos(filters=filters)
    else:
        # Use OpenAPI compatible approach
        result = await client.get_by_hex("4CA87C")
```

## Custom Configuration

### Custom Base URLs

Use a custom backend URL:

```python
# Custom RE-API instance
async with SkySnoop(
    backend="reapi",
    base_url="https://custom.re-api.url"
) as client:
    result = await client.get_by_hex("4CA87C")

# Custom OpenAPI instance
async with SkySnoop(
    backend="openapi",
    base_url="https://custom.api.url"
) as client:
    result = await client.get_by_hex("4CA87C")
```

### Custom Timeouts

Adjust request timeout for slow connections or large queries:

```python
# Increase timeout for bulk queries
async with SkySnoop(timeout=60.0) as client:
    result = await client.get_all_with_pos()  # May take longer
```

### API Key Configuration

For future OpenAPI authentication:

```python
# Via constructor
async with SkySnoop(api_key="your-api-key") as client:
    result = await client.get_by_hex("4CA87C")

# Via environment variable
import os
os.environ["SKYSNOOP_API_KEY"] = "your-api-key"

async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
```

## Error Handling Strategies

### Comprehensive Error Handling

```python
from skysnoop.exceptions import (
    SkySnoopError,
    APIError,
    TimeoutError,
    ValidationError,
    UnsupportedOperationError,
)

async with SkySnoop() as client:
    try:
        result = await client.get_by_hex("4CA87C")

    except UnsupportedOperationError as e:
        # Operation not available on current backend
        print(f"Operation not supported: {e}")
        # Try alternative or switch backend

    except ValidationError as e:
        # Invalid parameters
        print(f"Invalid input: {e}")
        # Fix parameters and retry

    except TimeoutError as e:
        # Request timed out
        print(f"Timeout: {e}")
        # Retry or increase timeout

    except APIError as e:
        # HTTP/API error
        print(f"API error: {e}")
        # Check backend status

    except SkySnoopError as e:
        # Base exception - catch-all
        print(f"Error: {e}")
```

### Retry Logic

```python
import asyncio
from skysnoop.exceptions import TimeoutError, APIError

async def query_with_retry(
    client,
    hex_code,
    max_retries=3,
    retry_delay=1.0
):
    """Query with automatic retry on transient errors."""
    for attempt in range(max_retries):
        try:
            return await client.get_by_hex(hex_code)

        except TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise

        except APIError as e:
            # Only retry on specific error codes
            if e.status_code in (429, 502, 503, 504):
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise
            else:
                # Don't retry on other errors
                raise

# Usage
async with SkySnoop() as client:
    result = await query_with_retry(client, "4CA87C")
```

### Fallback Backend

Automatically fall back to alternative backend on failure:

```python
async def query_with_fallback(hex_code):
    """Try RE-API first, fall back to OpenAPI."""
    try:
        async with SkySnoop(backend="reapi") as client:
            return await client.get_by_hex(hex_code)
    except (APIError, TimeoutError):
        # Fall back to OpenAPI
        async with SkySnoop(backend="openapi") as client:
            return await client.get_by_hex(hex_code)

# Usage
result = await query_with_fallback("4CA87C")
```

## Performance Optimization

### Connection Pooling

Reuse the same client for multiple requests:

```python
async with SkySnoop() as client:
    # Connection is pooled across requests
    result1 = await client.get_by_hex("4CA87C")
    result2 = await client.get_by_hex("ABC123")
    result3 = await client.get_by_callsign("UAL123")
    # Much faster than creating new client each time
```

### Concurrent Requests

Make multiple requests concurrently:

```python
import asyncio

async with SkySnoop() as client:
    # Run queries concurrently
    results = await asyncio.gather(
        client.get_by_hex("4CA87C"),
        client.get_by_hex("ABC123"),
        client.get_by_hex("DEF456"),
        client.get_by_callsign("UAL123"),
        client.get_in_circle(37.7749, -122.4194, 50),
    )

    for result in results:
        print(f"Found {result.result_count} aircraft")
```

### Batch Processing

Process large numbers of queries efficiently:

```python
async def batch_hex_queries(client, hex_codes, batch_size=10):
    """Query multiple hex codes in batches."""
    results = []

    for i in range(0, len(hex_codes), batch_size):
        batch = hex_codes[i:i+batch_size]

        # Process batch concurrently
        batch_results = await asyncio.gather(
            *[client.get_by_hex(hex_code) for hex_code in batch],
            return_exceptions=True
        )

        results.extend(batch_results)

    return results

# Usage
hex_codes = ["4CA87C", "ABC123", "DEF456", ...]
async with SkySnoop() as client:
    results = await batch_hex_queries(client, hex_codes)
```

### Caching Results

Implement simple caching for frequently accessed data:

```python
from datetime import datetime, timedelta

class CachedSkySnoop:
    """SkySnoop wrapper with simple caching."""

    def __init__(self, cache_ttl=60):
        self.cache = {}
        self.cache_ttl = cache_ttl

    async def get_by_hex_cached(self, client, hex_code):
        """Get aircraft with caching."""
        cache_key = f"hex:{hex_code}"

        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return result

        # Cache miss - query backend
        result = await client.get_by_hex(hex_code)

        # Store in cache
        self.cache[cache_key] = (result, datetime.now())

        return result

# Usage
cache = CachedSkySnoop(cache_ttl=60)

async with SkySnoop() as client:
    # First call - queries backend
    result1 = await cache.get_by_hex_cached(client, "4CA87C")

    # Second call within 60s - returns cached
    result2 = await cache.get_by_hex_cached(client, "4CA87C")
```

## Integration Patterns

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from skysnoop import SkySnoop

app = FastAPI()

# Create client at startup
@app.on_event("startup")
async def startup():
    app.state.skysnoop = SkySnoop()
    await app.state.skysnoop.__aenter__()

@app.on_event("shutdown")
async def shutdown():
    await app.state.skysnoop.__aexit__(None, None, None)

@app.get("/aircraft/{hex_code}")
async def get_aircraft(hex_code: str):
    try:
        result = await app.state.skysnoop.get_by_hex(hex_code)
        return {
            "count": result.result_count,
            "backend": result.backend,
            "aircraft": [
                {
                    "hex": ac.hex,
                    "flight": ac.flight,
                    "lat": ac.lat,
                    "lon": ac.lon,
                }
                for ac in result.aircraft
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Django Integration

```python
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from skysnoop import SkySnoop

# View function
async def aircraft_detail(request, hex_code):
    async with SkySnoop() as client:
        result = await client.get_by_hex(hex_code)

        return JsonResponse({
            "count": result.result_count,
            "aircraft": [
                {
                    "hex": ac.hex,
                    "flight": ac.flight,
                }
                for ac in result.aircraft
            ]
        })
```

### Background Task Processing

```python
import asyncio
from datetime import datetime

async def monitor_aircraft_worker():
    """Background worker to monitor aircraft."""
    async with SkySnoop() as client:
        while True:
            try:
                # Query aircraft
                result = await client.get_in_circle(
                    lat=37.7749,
                    lon=-122.4194,
                    radius=50
                )

                # Process results
                print(f"[{datetime.now()}] Found {result.result_count} aircraft")

                for aircraft in result.aircraft:
                    if aircraft.alt_baro and aircraft.alt_baro < 5000:
                        print(f"  Low altitude: {aircraft.flight} at {aircraft.alt_baro}ft")

                # Wait before next query
                await asyncio.sleep(60)

            except Exception as e:
                print(f"Error in worker: {e}")
                await asyncio.sleep(5)

# Run worker
asyncio.run(monitor_aircraft_worker())
```

## Testing Strategies

### Mocking SkySnoop

```python
from unittest.mock import AsyncMock, patch
from skysnoop.models.skydata import SkyData
from skysnoop.models.aircraft import Aircraft

@patch("my_module.SkySnoop")
async def test_my_function(mock_skysnoop_class):
    # Create mock client
    mock_client = AsyncMock()

    # Mock response
    mock_response = SkyData(
        result_count=1,
        timestamp=1234567890.0,
        backend="reapi",
        simulated=False,
        aircraft=[
            Aircraft(
                hex="4CA87C",
                flight="TEST123",
                lat=37.7749,
                lon=-122.4194,
            )
        ]
    )

    # Setup mock
    mock_client.get_by_hex.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_skysnoop_class.return_value = mock_client

    # Test your code
    result = await my_function()

    # Assertions
    assert result is not None
    mock_client.get_by_hex.assert_called_once_with("4CA87C")
```

### Testing with respx

```python
import pytest
import respx
from httpx import Response
from skysnoop import SkySnoop

@pytest.mark.asyncio
@respx.mock
async def test_skysnoop_query():
    # Mock API response
    mock_data = {
        "now": 1234567890.0,
        "resultCount": 1,
        "ptime": 10.5,
        "aircraft": [
            {
                "hex": "4CA87C",
                "flight": "TEST123",
                "lat": 37.7749,
                "lon": -122.4194,
            }
        ]
    }

    # Setup mock route
    respx.get(url__regex=r".*\?find_hex=4CA87C").mock(
        return_value=Response(200, json=mock_data)
    )

    # Test
    async with SkySnoop(backend="reapi") as client:
        result = await client.get_by_hex("4CA87C")

    assert result.result_count == 1
    assert result.aircraft[0].hex == "4CA87C"
```

## Environment Configuration

### Using Environment Variables

```bash
# ~/.bashrc or ~/.zshrc

# Backend selection
export SKYSNOOP_BACKEND="reapi"

# API key (future)
export SKYSNOOP_API_KEY="your-api-key"

# Custom URLs
export ADSB_API_BASE_URL="https://custom.api.url"
export REAPI_BASE_URL="https://custom.re-api.url"

# Timeouts
export ADSB_API_TIMEOUT="60"

# Logging
export SKYSNOOP_LOG_LEVEL="DEBUG"
```

### Loading from .env File

```python
from dotenv import load_dotenv
from skysnoop import SkySnoop

# Load environment variables from .env file
load_dotenv()

# Configuration automatically loaded from environment
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
```

## Debugging

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async with SkySnoop() as client:
    # Detailed logs about backend selection, requests, etc.
    result = await client.get_by_hex("4CA87C")
```

### Inspect Raw Responses

Use low-level clients to see raw API responses:

```python
from skysnoop.client import ReAPIClient

async with ReAPIClient() as client:
    response = await client.find_hex("4CA87C")

    # Access raw response data
    print(f"Raw result count: {response.resultCount}")
    print(f"Processing time: {response.ptime}ms")
    print(f"Raw aircraft data: {response.aircraft[0]}")
```

## Next Steps

- **Back to basics**: [Getting Started](./getting-started.md)
- **Client reference**: [SkySnoop Client Guide](./skysnoop-client.md)
- **Developer docs**: [Developer Documentation](./dev/README.md)
