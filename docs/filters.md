# Query Filters

Query filters allow you to refine aircraft searches by altitude, type, callsign, and more. Filters are **only supported on the RE-API backend**.

## Quick Reference

```python
from skysnoop import SkySnoop
from skysnoop.query.filters import QueryFilters

async with SkySnoop(backend="reapi") as client:
    filters = QueryFilters(
        callsign_exact="UAL123",
        type_code="B738",
        above_alt_baro=10000,
        below_alt_baro=40000,
        military=True,
    )

    result = await client.get_in_circle(
        lat=37.7749,
        lon=-122.4194,
        radius=100,
        filters=filters
    )
```

## Important Notes

### RE-API Only

**Filters are only supported on the RE-API backend.** Using filters with OpenAPI will:

- Log a warning message
- Ignore the filters
- Return unfiltered results

```python
# ✅ Correct - explicitly use RE-API
async with SkySnoop(backend="reapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)

# ⚠️ Warning - filters ignored on OpenAPI
async with SkySnoop(backend="openapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)
    # Filters are ignored with warning
```

### Not All Methods Support Filters

Filters are supported on these methods:

- ✅ `get_in_circle()`
- ✅ `get_closest()`
- ✅ `get_in_box()`
- ✅ `get_all()`
- ✅ `get_all_with_pos()`

Filters are **not** supported on identifier queries:

- ❌ `get_by_hex()`
- ❌ `get_by_callsign()`
- ❌ `get_by_registration()`
- ❌ `get_by_type()`

## Available Filters

### Callsign Filters

#### callsign_exact

Match exact callsign (case-sensitive).

```python
filters = QueryFilters(callsign_exact="UAL123")
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Example matches**: "UAL123"
**Example non-matches**: "UAL124", "UAL1230", "ual123"

#### callsign_prefix

Match callsigns starting with prefix (case-sensitive).

```python
filters = QueryFilters(callsign_prefix="UAL")
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Example matches**: "UAL123", "UAL456", "UAL999"
**Example non-matches**: "UAAL123", "AAL123", "ual123"

### Aircraft Type Filter

#### type_code

Filter by ICAO aircraft type designator.

```python
# Find all Boeing 737-800s
filters = QueryFilters(type_code="B738")
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Common type codes**:

- `B738` - Boeing 737-800
- `B77W` - Boeing 777-300ER
- `A320` - Airbus A320
- `A388` - Airbus A380-800
- `B752` - Boeing 757-200
- `CRJ9` - Bombardier CRJ-900

### Altitude Filters

#### above_alt_baro

Filter to aircraft above a certain altitude (feet, barometric).

```python
# Only aircraft above 10,000 feet
filters = QueryFilters(above_alt_baro=10000)
result = await client.get_in_circle(lat, lon, radius, filters)
```

#### below_alt_baro

Filter to aircraft below a certain altitude (feet, barometric).

```python
# Only aircraft below 30,000 feet
filters = QueryFilters(below_alt_baro=30000)
result = await client.get_in_circle(lat, lon, radius, filters)
```

#### Altitude Range

Combine both filters for a range:

```python
# Aircraft between 10,000 and 30,000 feet
filters = QueryFilters(
    above_alt_baro=10000,
    below_alt_baro=30000
)
result = await client.get_in_circle(lat, lon, radius, filters)
```

### Special Category Filters

#### military

Filter to military aircraft only.

```python
filters = QueryFilters(military=True)
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Note**: Identifies aircraft with military designations. May not catch all military aircraft.

#### interesting

Filter to "interesting" aircraft (special designations, rare types, etc.).

```python
filters = QueryFilters(interesting=True)
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Note**: The definition of "interesting" is determined by the adsb.lol backend.

### Squawk Code Filter

#### squawk

Filter by transponder squawk code.

```python
# Emergency squawk
filters = QueryFilters(squawk="7700")
result = await client.get_in_circle(lat, lon, radius, filters)
```

**Common squawk codes**:

- `7700` - Emergency
- `7600` - Radio failure
- `7500` - Hijacking
- `1200` - VFR (US)
- `7000` - VFR (Europe)

## Combining Filters

You can combine multiple filters to create complex queries:

### Example: High-altitude Boeing 737s

```python
filters = QueryFilters(
    type_code="B738",
    above_alt_baro=30000,
    below_alt_baro=42000
)
result = await client.get_in_circle(lat, lon, radius, filters)
```

### Example: United Airlines flights at cruise

```python
filters = QueryFilters(
    callsign_prefix="UAL",
    above_alt_baro=28000,
    below_alt_baro=41000
)
result = await client.get_in_circle(lat, lon, radius, filters)
```

### Example: Military aircraft in area

```python
filters = QueryFilters(
    military=True,
    above_alt_baro=5000  # Exclude ground traffic
)
result = await client.get_in_circle(lat, lon, radius, filters)
```

## Filter Behavior

### AND Logic

All specified filters are combined with AND logic:

```python
filters = QueryFilters(
    type_code="B738",
    above_alt_baro=30000
)
# Returns aircraft that are BOTH B738 AND above 30,000 feet
```

### None/Empty Values

Filters with `None` or default values are ignored:

```python
filters = QueryFilters(
    callsign_exact=None,     # Ignored
    above_alt_baro=None,     # Ignored
    type_code="B738"         # Applied
)
```

### Checking Active Filters

Check if any filters are active:

```python
filters = QueryFilters(type_code="B738")
if filters.has_filters:
    print("Filters are active")
```

## Using Filters with Different Methods

### Geographic Queries

Filters work with all geographic query methods:

```python
filters = QueryFilters(military=True)

# Circle search
result = await client.get_in_circle(
    lat=37.7749, lon=-122.4194, radius=50, filters=filters
)

# Closest aircraft
result = await client.get_closest(
    lat=37.7749, lon=-122.4194, radius=100, filters=filters
)

# Bounding box
result = await client.get_in_box(
    lat_min=37.0, lat_max=38.0,
    lon_min=-123.0, lon_max=-122.0,
    filters=filters
)
```

### Bulk Queries

Filters work with bulk queries:

```python
filters = QueryFilters(
    above_alt_baro=10000,
    type_code="B738"
)

# All aircraft with position
result = await client.get_all_with_pos(filters=filters)

# All tracked aircraft
result = await client.get_all(filters=filters)
```

## Common Use Cases

### Monitor Specific Airline

```python
async def monitor_airline(client, airline_code):
    """Monitor all flights for a specific airline."""
    filters = QueryFilters(
        callsign_prefix=airline_code,
        above_alt_baro=1000  # Exclude ground
    )

    result = await client.get_all_with_pos(filters=filters)
    return result

# Usage
async with SkySnoop(backend="reapi") as client:
    united = await monitor_airline(client, "UAL")
    print(f"United flights: {united.result_count}")
```

### Find Aircraft by Type in Area

```python
async def find_type_in_area(client, aircraft_type, lat, lon, radius):
    """Find specific aircraft type near a location."""
    filters = QueryFilters(type_code=aircraft_type)

    result = await client.get_in_circle(lat, lon, radius, filters)
    return result

# Usage
async with SkySnoop(backend="reapi") as client:
    # Find all A380s within 100nm of LAX
    a380s = await find_type_in_area(client, "A388", 33.9416, -118.4085, 100)
    print(f"Found {a380s.result_count} A380s")
```

### Track Emergency Aircraft

```python
async def find_emergencies(client):
    """Find aircraft declaring emergencies."""
    filters = QueryFilters(squawk="7700")

    result = await client.get_all_with_pos(filters=filters)
    return result

# Usage
async with SkySnoop(backend="reapi") as client:
    emergencies = await find_emergencies(client)

    for aircraft in emergencies.aircraft:
        print(f"Emergency: {aircraft.flight} at {aircraft.lat}, {aircraft.lon}")
```

### Find Departing/Arriving Aircraft

```python
async def find_departures(client, airport_lat, airport_lon):
    """Find aircraft departing (climbing below 10,000ft)."""
    filters = QueryFilters(
        above_alt_baro=100,   # Not on ground
        below_alt_baro=10000  # Below 10,000ft
    )

    result = await client.get_in_circle(
        lat=airport_lat,
        lon=airport_lon,
        radius=25,  # 25nm from airport
        filters=filters
    )

    # Further filter by vertical rate (climbing)
    departures = [
        ac for ac in result.aircraft
        if ac.baro_rate and ac.baro_rate > 500  # Climbing
    ]

    return departures

# Usage
async with SkySnoop(backend="reapi") as client:
    # Departures from SFO
    departures = await find_departures(client, 37.6213, -122.3790)
    print(f"Found {len(departures)} departing aircraft")
```

## Performance Considerations

### Server-Side Filtering

Filters are applied **server-side** by the RE-API backend, which means:

- ✅ Reduces data transfer
- ✅ Faster query performance
- ✅ More efficient than client-side filtering

### When to Use Filters

**Use filters when**:

- You need specific subsets of aircraft
- Working with large geographic areas
- Performance is important
- You want to reduce data transfer

**Don't use filters when**:

- You need all aircraft (filters add overhead)
- Using OpenAPI backend (not supported)
- You need complex OR logic (not supported)
- You need to filter by fields not supported

## Client-Side Filtering

For more complex filtering not supported by QueryFilters, filter results yourself:

```python
result = await client.get_in_circle(lat, lon, radius)

# Client-side filtering for complex logic
filtered = [
    ac for ac in result.aircraft
    if (
        ac.alt_baro and 10000 < ac.alt_baro < 20000
        and ac.gs and ac.gs > 200
        and ac.type and ac.type.startswith("B7")  # All Boeing 7-series
    )
]

print(f"Found {len(filtered)} matching aircraft")
```

## Error Handling

Filters don't typically raise errors, but watch for warnings:

```python
import logging

logging.basicConfig(level=logging.WARNING)

# This will log a warning with OpenAPI
async with SkySnoop(backend="openapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)
    # Warning: QueryFilters not supported by OpenAPI backend, ignoring
```

## QueryFilters Reference

### Constructor

```python
QueryFilters(
    callsign_exact: str | None = None,
    callsign_prefix: str | None = None,
    type_code: str | None = None,
    squawk: str | None = None,
    above_alt_baro: int | None = None,
    below_alt_baro: int | None = None,
    military: bool | None = None,
    interesting: bool | None = None,
)
```

### Properties

```python
filters = QueryFilters(type_code="B738")

# Check if any filters are active
filters.has_filters  # bool
```

### Validation

QueryFilters validates input:

```python
from skysnoop.exceptions import ValidationError

try:
    # Invalid altitude (negative)
    filters = QueryFilters(above_alt_baro=-1000)
except ValidationError as e:
    print(f"Invalid filter: {e}")
```

## Best Practices

### DO ✅

**Use filters to reduce data transfer**:

```python
# Good - filter server-side
filters = QueryFilters(type_code="B738")
result = await client.get_all_with_pos(filters=filters)
```

**Combine filters for precision**:

```python
filters = QueryFilters(
    callsign_prefix="UAL",
    above_alt_baro=20000,
    below_alt_baro=42000
)
```

**Check backend before using filters**:

```python
if client.backend_type == "reapi":
    filters = QueryFilters(military=True)
else:
    filters = None
```

### DON'T ❌

**Don't use filters with OpenAPI**:

```python
# Bad - filters ignored
async with SkySnoop(backend="openapi") as client:
    filters = QueryFilters(military=True)
    result = await client.get_in_circle(lat, lon, radius, filters)
```

**Don't use filters on identifier queries**:

```python
# Bad - filters have no effect
filters = QueryFilters(military=True)
result = await client.get_by_hex("4CA87C", filters=filters)
# Error: get_by_hex() doesn't accept filters parameter
```

**Don't rely on filters for complex logic**:

```python
# Bad - OR logic not supported
# Can't express: (type=B738 OR type=B739)
```

## Next Steps

- **Back to**: [SkySnoop Client Guide](./skysnoop-client.md)
- **Advanced usage**: [Advanced Usage Guide](./advanced.md)
- **CLI filtering**: [CLI Usage](./cli-usage.md)
