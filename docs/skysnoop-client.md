# SkySnoop Client Guide

The `SkySnoop` client is the **recommended interface** for querying aircraft data from adsb.lol. It provides a unified API that works with both OpenAPI and RE-API backends, automatically handling differences and normalizing responses.

## Quick Reference

```python
from skysnoop import SkySnoop

async with SkySnoop() as client:
    # Identifier queries
    await client.get_by_hex("4CA87C")
    await client.get_by_callsign("UAL123")
    await client.get_by_registration("N12345")
    await client.get_by_type("B738")

    # Geographic queries
    await client.get_in_circle(lat, lon, radius)
    await client.get_closest(lat, lon, radius)
    await client.get_in_box(lat_min, lat_max, lon_min, lon_max)

    # Bulk queries (RE-API only)
    await client.get_all()
    await client.get_all_with_pos()
```

## Identifier Queries

### get_by_hex()

Find aircraft by ICAO 24-bit hex code.

```python
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")

    if result.has_results:
        aircraft = result.aircraft[0]
        print(f"{aircraft.hex}: {aircraft.flight}")
```

**Parameters**:

- `hex_code` (str): ICAO hex identifier (e.g., "4CA87C")

**Returns**: `SkyData` with matching aircraft

**Backend Support**: RE-API ✅ | OpenAPI ✅

### get_by_callsign()

Find aircraft by callsign/flight number.

```python
async with SkySnoop() as client:
    result = await client.get_by_callsign("UAL123")

    for aircraft in result.aircraft:
        print(f"{aircraft.flight}: {aircraft.registration}")
```

**Parameters**:

- `callsign` (str): Aircraft callsign (e.g., "UAL123")

**Returns**: `SkyData` with matching aircraft (may be multiple)

**Backend Support**: RE-API ✅ | OpenAPI ✅

### get_by_registration()

Find aircraft by registration (tail number).

```python
async with SkySnoop() as client:
    result = await client.get_by_registration("N12345")
```

**Parameters**:

- `registration` (str): Aircraft registration (e.g., "N12345")

**Returns**: `SkyData` with matching aircraft

**Backend Support**: RE-API ✅ | OpenAPI ✅

### get_by_type()

Find aircraft by type designator.

```python
async with SkySnoop() as client:
    # Find all Boeing 737-800s
    result = await client.get_by_type("B738")

    print(f"Found {result.result_count} B738 aircraft")
```

**Parameters**:

- `aircraft_type` (str): ICAO type code (e.g., "B738", "A320", "B77W")

**Returns**: `SkyData` with matching aircraft

**Backend Support**: RE-API ✅ | OpenAPI ✅

## Geographic Queries

### get_in_circle()

Find all aircraft within a circular area.

```python
async with SkySnoop() as client:
    # Aircraft within 50nm of San Francisco
    result = await client.get_in_circle(
        lat=37.7749,
        lon=-122.4194,
        radius=50  # nautical miles
    )

    print(f"Found {result.result_count} aircraft")
```

**Parameters**:

- `lat` (float): Center latitude in decimal degrees
- `lon` (float): Center longitude in decimal degrees
- `radius` (float): Search radius in nautical miles
- `filters` (QueryFilters | None): Optional filters (RE-API only)

**Returns**: `SkyData` with aircraft in the area

**Backend Support**: RE-API ✅ (native) | OpenAPI ⚠️ (simulated)

**Note**: OpenAPI simulates this operation by fetching and filtering. Check `result.simulated` flag.

### get_closest()

Find the single closest aircraft to a point.

```python
async with SkySnoop() as client:
    # Find aircraft closest to JFK airport
    result = await client.get_closest(
        lat=40.6413,
        lon=-73.7781,
        radius=100  # search within 100nm
    )

    if result.has_results:
        aircraft = result.aircraft[0]
        print(f"Closest: {aircraft.flight} at {aircraft.alt_baro}ft")
```

**Parameters**:

- `lat` (float): Center latitude
- `lon` (float): Center longitude
- `radius` (float): Maximum search radius in nautical miles
- `filters` (QueryFilters | None): Optional filters

**Returns**: `SkyData` with the closest aircraft (empty if none found)

**Backend Support**: RE-API ✅ (native) | OpenAPI ⚠️ (simulated)

### get_in_box()

Find all aircraft within a rectangular bounding box.

```python
async with SkySnoop() as client:
    # Aircraft in the San Francisco Bay Area
    result = await client.get_in_box(
        lat_min=37.0,
        lat_max=38.5,
        lon_min=-123.0,
        lon_max=-121.5
    )
```

**Parameters**:

- `lat_min` (float): Southern boundary
- `lat_max` (float): Northern boundary
- `lon_min` (float): Western boundary
- `lon_max` (float): Eastern boundary
- `filters` (QueryFilters | None): Optional filters

**Returns**: `SkyData` with aircraft in the box

**Backend Support**: RE-API ✅ (native) | OpenAPI ⚠️ (simulated)

## Bulk Queries

### get_all()

Get all tracked aircraft (with or without position data).

```python
async with SkySnoop(backend="reapi") as client:
    result = await client.get_all()
    print(f"Total aircraft: {result.result_count}")
```

**Parameters**:

- `filters` (QueryFilters | None): Optional filters

**Returns**: `SkyData` with all aircraft

**Backend Support**: RE-API ✅ | OpenAPI ❌ (raises `UnsupportedOperationError`)

**Note**: Only available on RE-API backend. OpenAPI doesn't support global queries.

### get_all_with_pos()

Get all aircraft that have position data.

```python
async with SkySnoop(backend="reapi") as client:
    result = await client.get_all_with_pos()

    # Filter to aircraft with altitude
    airborne = [
        ac for ac in result.aircraft
        if ac.alt_baro and ac.alt_baro > 0
    ]
    print(f"Airborne: {len(airborne)}")
```

**Parameters**:

- `filters` (QueryFilters | None): Optional filters

**Returns**: `SkyData` with aircraft that have position

**Backend Support**: RE-API ✅ | OpenAPI ❌

## Response Structure

All methods return a `SkyData` object:

```python
result = await client.get_by_hex("4CA87C")

# Metadata
result.result_count      # int: Number of aircraft
result.timestamp         # float: Query timestamp (seconds since epoch)
result.backend           # str: "reapi" or "openapi"
result.simulated         # bool: True if operation was simulated
result.processing_time   # float | None: Processing time in ms (RE-API only)

# Aircraft data
result.aircraft          # List[Aircraft]: List of aircraft objects

# Convenience properties
result.count             # Alias for result_count
result.has_results       # bool: True if result_count > 0

# Iteration
for aircraft in result.aircraft:
    print(aircraft.hex)

# Length
print(len(result.aircraft))
```

## Aircraft Model

Each aircraft in `result.aircraft` is an `Aircraft` object:

```python
aircraft = result.aircraft[0]

# Identification
aircraft.hex             # str: ICAO 24-bit hex (always present)
aircraft.flight          # str | None: Callsign/flight number
aircraft.registration    # str | None: Tail number
aircraft.type            # str | None: Aircraft type code
aircraft.squawk          # str | None: Transponder squawk code

# Position
aircraft.lat             # float | None: Latitude
aircraft.lon             # float | None: Longitude
aircraft.alt_baro        # int | None: Barometric altitude (feet)
aircraft.alt_geom        # int | None: Geometric altitude (feet)

# Movement
aircraft.gs              # float | None: Ground speed (knots)
aircraft.track           # float | None: Track/heading (degrees)
aircraft.baro_rate       # int | None: Vertical rate (ft/min)
aircraft.ias             # int | None: Indicated airspeed
aircraft.tas             # int | None: True airspeed

# Status
aircraft.seen            # float | None: Seconds since last update
aircraft.seen_pos        # float | None: Seconds since position update
aircraft.emergency       # str | None: Emergency status
aircraft.category        # str | None: Aircraft category

# ... many more fields available
```

**Note**: Most fields are optional (`None` if not available). Always check before using:

```python
if aircraft.lat is not None and aircraft.lon is not None:
    print(f"Position: {aircraft.lat}, {aircraft.lon}")
```

## Query Filters

Use `QueryFilters` to refine searches (RE-API only):

```python
from skysnoop.query.filters import QueryFilters

async with SkySnoop(backend="reapi") as client:
    filters = QueryFilters(
        # Callsign filters
        callsign_exact="UAL123",        # Exact match
        callsign_prefix="UAL",          # Starts with

        # Aircraft type
        type_code="B738",               # Type designator

        # Altitude filters
        above_alt_baro=10000,           # Above 10,000 feet
        below_alt_baro=30000,           # Below 30,000 feet

        # Special categories
        military=True,                  # Military aircraft only
        interesting=True,               # Interesting aircraft only

        # Squawk code
        squawk="7700",                  # Emergency squawk
    )

    result = await client.get_in_circle(
        lat=37.7749,
        lon=-122.4194,
        radius=100,
        filters=filters
    )
```

**See**: [Query Filters Guide](./filters.md) for complete filter documentation.

**Important**: Filters are **only supported on RE-API backend**. Using filters with OpenAPI will log a warning and ignore them.

## Backend Selection

### Automatic (Recommended)

```python
# Default - automatically selects best backend
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")

print(f"Used backend: {result.backend}")
```

**Auto-selection logic**:

1. If API key provided → OpenAPI
2. Otherwise → RE-API (preferred)

### Explicit Selection

```python
# Force RE-API (feeder access required)
async with SkySnoop(backend="reapi") as client:
    result = await client.get_all()  # Only available on RE-API

# Force OpenAPI (public access)
async with SkySnoop(backend="openapi") as client:
    result = await client.get_by_hex("4CA87C")
```

### Backend Comparison

| Feature | RE-API | OpenAPI |
|---------|--------|---------|
| **Access** | Feeder-only | Public |
| **Identifier queries** | ✅ Native | ✅ Native |
| **Geographic queries** | ✅ Native | ⚠️ Simulated |
| **Bulk queries** | ✅ Supported | ❌ Not available |
| **Query filters** | ✅ Full support | ❌ Not supported |
| **Performance** | Fast | Slower for geographic queries |

## Configuration Options

```python
async with SkySnoop(
    backend="auto",              # "auto", "reapi", or "openapi"
    api_key=None,                # API key (for future OpenAPI auth)
    base_url=None,               # Custom base URL
    timeout=30.0                 # Request timeout in seconds
) as client:
    result = await client.get_by_hex("4CA87C")
```

### Environment Variables

Configure via environment:

```bash
# API key (future use)
export SKYSNOOP_API_KEY="your-api-key"

# Custom base URL
export ADSB_API_BASE_URL="https://custom.api.url"

# Request timeout
export ADSB_API_TIMEOUT="60"
```

## Error Handling

### UnsupportedOperationError

Raised when operation not available on current backend:

```python
from skysnoop.exceptions import UnsupportedOperationError

async with SkySnoop(backend="openapi") as client:
    try:
        result = await client.get_all()
    except UnsupportedOperationError:
        print("get_all() not available on OpenAPI backend")
        # Try alternative or switch to RE-API
```

### Other Exceptions

```python
from skysnoop.exceptions import (
    SkySnoopError,          # Base exception
    APIError,               # HTTP/API errors
    TimeoutError,           # Request timeouts
    ValidationError,        # Invalid parameters
)

try:
    result = await client.get_by_hex("INVALID")
except ValidationError as e:
    print(f"Invalid parameter: {e}")
except TimeoutError:
    print("Request timed out")
except APIError as e:
    print(f"API error: {e}")
except SkySnoopError as e:
    print(f"Error: {e}")
```

## Best Practices

### DO ✅

**Use async context manager**:

```python
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
```

**Check for results before accessing**:

```python
if result.has_results:
    aircraft = result.aircraft[0]
```

**Handle None values**:

```python
if aircraft.lat is not None and aircraft.lon is not None:
    print(f"Position: {aircraft.lat}, {aircraft.lon}")
```

**Use default auto backend**:

```python
async with SkySnoop() as client:  # Let it choose
    result = await client.get_by_hex("4CA87C")
```

**Check simulated flag for critical applications**:

```python
result = await client.get_in_circle(37.7749, -122.4194, 50)
if result.simulated:
    print("Warning: Geographic query was simulated")
```

### DON'T ❌

**Don't forget cleanup**:

```python
# ❌ Wrong - no cleanup
client = SkySnoop()
result = await client.get_by_hex("4CA87C")
# Forgot to close!

# ✅ Correct - automatic cleanup
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
```

**Don't rely on filters with OpenAPI**:

```python
# ❌ Wrong - filters ignored on OpenAPI
async with SkySnoop(backend="openapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)

# ✅ Correct - use RE-API for filters
async with SkySnoop(backend="reapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)
```

**Don't assume all fields are present**:

```python
# ❌ Wrong - may be None
altitude = aircraft.alt_baro + 1000

# ✅ Correct - check first
if aircraft.alt_baro is not None:
    altitude = aircraft.alt_baro + 1000
```

## Common Patterns

### Multiple Concurrent Queries

```python
import asyncio

async with SkySnoop() as client:
    results = await asyncio.gather(
        client.get_by_hex("4CA87C"),
        client.get_by_hex("ABC123"),
        client.get_by_callsign("UAL123"),
    )

    for result in results:
        print(f"Found {result.result_count} aircraft")
```

### Retry on Timeout

```python
from skysnoop.exceptions import TimeoutError

async def query_with_retry(client, hex_code, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.get_by_hex(hex_code)
        except TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait before retry
            else:
                raise
```

### Filter Empty Positions

```python
result = await client.get_all_with_pos()

# Only aircraft with valid positions
positioned = [
    ac for ac in result.aircraft
    if ac.lat is not None and ac.lon is not None
]
```

## Next Steps

- **Learn about filtering**: [Query Filters Guide](./filters.md)
- **Advanced usage**: [Advanced Usage Guide](./advanced.md)
- **CLI reference**: [CLI Usage](./cli-usage.md)
- **Developer docs**: [Developer Documentation](./dev/README.md)
