# Getting Started with SkySnoop

This guide will help you get up and running with SkySnoop quickly.

## Installation

### Requirements

- Python 3.10 or higher
- pip package manager

### Install from PyPI

```bash
pip install skysnoop
```

### Install from Source

```bash
git clone https://github.com/tedivm/skysnoop.git
cd skysnoop
pip install -e .
```

### Verify Installation

```bash
skysnoop --version
```

## Your First Query

Let's start with a simple example that finds aircraft by their ICAO hex code:

```python
import asyncio
from skysnoop import SkySnoop

async def main():
    # Create a SkySnoop client
    async with SkySnoop() as client:
        # Query for aircraft with hex code 4CA87C
        result = await client.get_by_hex("4CA87C")

        # Print results
        print(f"Found {result.result_count} aircraft")
        print(f"Backend used: {result.backend}")

        # Show aircraft details
        for aircraft in result.aircraft:
            print(f"  Hex: {aircraft.hex}")
            print(f"  Callsign: {aircraft.flight}")
            print(f"  Altitude: {aircraft.alt_baro} feet")

# Run the async function
asyncio.run(main())
```

Save this as `example.py` and run it:

```bash
python example.py
```

## Understanding the Basics

### Async/Await

SkySnoop uses Python's async/await syntax for better performance:

```python
# Define async function
async def main():
    # Use async context manager
    async with SkySnoop() as client:
        # Await async operations
        result = await client.get_by_hex("4CA87C")

# Run with asyncio
asyncio.run(main())
```

**Why async?** Async code allows multiple requests to run concurrently, which is much faster when making multiple API calls.

### Context Managers

Always use `async with` to ensure proper cleanup:

```python
# ✅ Correct - automatic cleanup
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
# Client is automatically closed here

# ❌ Avoid - manual cleanup required
client = SkySnoop()
result = await client.get_by_hex("4CA87C")
await client.close()  # Easy to forget!
```

### Response Structure

All queries return a `SkyData` object:

```python
result = await client.get_by_hex("4CA87C")

# Access metadata
result.result_count   # Number of aircraft found
result.timestamp      # Query timestamp
result.backend        # Backend used ("reapi" or "openapi")
result.simulated      # Whether operation was simulated

# Access aircraft
result.aircraft       # List of Aircraft objects

# Iterate over aircraft
for aircraft in result.aircraft:
    print(aircraft.hex)
```

## Common Query Types

### Find Aircraft by Identifier

```python
async with SkySnoop() as client:
    # By ICAO hex code
    result = await client.get_by_hex("4CA87C")

    # By callsign/flight number
    result = await client.get_by_callsign("UAL123")

    # By registration (tail number)
    result = await client.get_by_registration("N12345")

    # By aircraft type
    result = await client.get_by_type("B738")  # Boeing 737-800
```

### Find Aircraft by Location

```python
async with SkySnoop() as client:
    # Aircraft within 50nm of San Francisco
    result = await client.get_in_circle(
        lat=37.7749,
        lon=-122.4194,
        radius=50  # nautical miles
    )

    # Closest aircraft within 100nm
    result = await client.get_closest(
        lat=37.7749,
        lon=-122.4194,
        radius=100
    )

    # Aircraft in a bounding box
    result = await client.get_in_box(
        lat_min=37.0,
        lat_max=38.0,
        lon_min=-123.0,
        lon_max=-122.0
    )
```

## Working with Aircraft Data

The `Aircraft` model contains all available information about an aircraft:

```python
result = await client.get_by_hex("4CA87C")

for aircraft in result.aircraft:
    # Identification
    print(f"Hex: {aircraft.hex}")
    print(f"Flight: {aircraft.flight}")
    print(f"Registration: {aircraft.registration}")
    print(f"Type: {aircraft.type}")

    # Position
    print(f"Latitude: {aircraft.lat}")
    print(f"Longitude: {aircraft.lon}")
    print(f"Altitude: {aircraft.alt_baro} feet")

    # Movement
    print(f"Ground speed: {aircraft.gs} knots")
    print(f"Track: {aircraft.track}°")
    print(f"Vertical rate: {aircraft.baro_rate} ft/min")

    # Note: Not all fields are always available
    # Check for None before using
    if aircraft.lat is not None and aircraft.lon is not None:
        print(f"Position: {aircraft.lat}, {aircraft.lon}")
```

## Using the CLI

SkySnoop includes a command-line interface for quick queries:

```bash
# Find aircraft by hex
skysnoop hex 4CA87C

# Search near San Francisco (50nm radius)
skysnoop circle 37.7749 -122.4194 50

# Find closest aircraft
skysnoop closest 37.7749 -122.4194 100

# Get output as JSON
skysnoop hex 4CA87C --output json

# Use table format (default)
skysnoop circle 37.7749 -122.4194 50 --output table
```

See [CLI Usage](./cli-usage.md) for complete CLI documentation.

## Backend Selection

SkySnoop supports two backends:

- **RE-API**: Feeder-only, full features (default)
- **OpenAPI**: Public access, some features simulated

### Automatic Selection (Recommended)

```python
# Automatically selects the best backend
async with SkySnoop() as client:
    result = await client.get_by_hex("4CA87C")
```

**Auto-selection logic**:

1. If API key provided → OpenAPI
2. Otherwise → RE-API (preferred for full features)

### Manual Selection

```python
# Force RE-API backend
async with SkySnoop(backend="reapi") as client:
    result = await client.get_by_hex("4CA87C")

# Force OpenAPI backend
async with SkySnoop(backend="openapi") as client:
    result = await client.get_by_hex("4CA87C")
```

### Backend Differences

| Feature | RE-API | OpenAPI |
|---------|--------|---------|
| Access | Feeder-only | Public |
| Geographic queries | Native | Simulated |
| Filters | Full support | Not supported |
| Bulk queries | Supported | Not supported |

Most users won't need to worry about backends—the default auto-selection works well.

## Error Handling

Always handle potential errors:

```python
from skysnoop.exceptions import (
    SkySnoopError,
    APIError,
    TimeoutError,
    UnsupportedOperationError,
)

async with SkySnoop() as client:
    try:
        result = await client.get_by_hex("4CA87C")

    except UnsupportedOperationError:
        print("This operation isn't supported on the current backend")

    except TimeoutError:
        print("Request timed out - try again")

    except APIError as e:
        print(f"API error: {e}")

    except SkySnoopError as e:
        print(f"General error: {e}")
```

## Configuration

### Environment Variables

Set configuration via environment variables:

```bash
# API key (for future use)
export SKYSNOOP_API_KEY="your-api-key"

# Custom base URL
export ADSB_API_BASE_URL="https://custom.api.url"

# Request timeout (seconds)
export ADSB_API_TIMEOUT="60"
```

### Programmatic Configuration

```python
async with SkySnoop(
    backend="auto",              # Backend selection
    api_key=None,                # API key (future)
    base_url=None,               # Custom base URL
    timeout=30.0                 # Request timeout
) as client:
    result = await client.get_by_hex("4CA87C")
```

## Next Steps

Now that you understand the basics:

- **Learn about filtering**: [Query Filters](./filters.md)
- **Explore all methods**: [SkySnoop Client Guide](./skysnoop-client.md)
- **Advanced features**: [Advanced Usage](./advanced.md)
- **CLI reference**: [CLI Usage](./cli-usage.md)

## Common Patterns

### Multiple Concurrent Queries

```python
import asyncio

async with SkySnoop() as client:
    # Run multiple queries concurrently
    results = await asyncio.gather(
        client.get_by_hex("4CA87C"),
        client.get_by_hex("ABC123"),
        client.get_by_callsign("UAL123"),
    )

    for result in results:
        print(f"Found {result.result_count} aircraft")
```

### Periodic Monitoring

```python
import asyncio

async def monitor_location():
    async with SkySnoop() as client:
        while True:
            result = await client.get_in_circle(
                lat=37.7749,
                lon=-122.4194,
                radius=50
            )
            print(f"Found {result.result_count} aircraft")

            # Wait 60 seconds before next query
            await asyncio.sleep(60)

asyncio.run(monitor_location())
```

### Checking for Empty Results

```python
result = await client.get_by_hex("UNKNOWN")

if result.has_results:
    print(f"Found {result.result_count} aircraft")
    for aircraft in result.aircraft:
        print(aircraft.hex)
else:
    print("No aircraft found")
```

## Troubleshooting

### Import Error

```
ModuleNotFoundError: No module named 'skysnoop'
```

**Solution**: Install the package with `pip install skysnoop`

### Async Error

```
RuntimeError: This event loop is already running
```

**Solution**: Use `asyncio.run()` at the top level, not within an existing event loop

### Timeout Error

```
TimeoutError: Request timed out after 30 seconds
```

**Solution**: Increase timeout:

```python
async with SkySnoop(timeout=60.0) as client:
    result = await client.get_all()  # May take longer
```

### No Results

If you're not getting results:

1. Check that hex code/callsign is correct
2. Verify aircraft is currently airborne and reporting
3. For location queries, ensure radius is large enough
4. Try a different backend: `SkySnoop(backend="openapi")`

## Getting Help

- **Documentation**: [docs/README.md](./README.md)
- **Issues**: [GitHub Issues](https://github.com/tedivm/skysnoop/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tedivm/skysnoop/discussions)
