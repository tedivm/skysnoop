# SkySnoop Documentation

Welcome to the SkySnoop documentation! SkySnoop is a Python SDK and CLI for querying aircraft data from [adsb.lol](https://adsb.lol).

## Quick Start

### Installation

```bash
pip install skysnoop
```

### Basic Example

```python
import asyncio
from skysnoop import SkySnoop

async def main():
    async with SkySnoop() as client:
        # Find aircraft by hex code
        result = await client.get_by_hex("4CA87C")
        print(f"Found {result.result_count} aircraft")

asyncio.run(main())
```

## Documentation Structure

### User Documentation (You Are Here)

**Start here if you want to use SkySnoop in your application:**

- **[Getting Started](./getting-started.md)** - Installation, quick start, and basic concepts
- **[SkySnoop Client Guide](./skysnoop-client.md)** - Complete guide to the high-level unified client (recommended for most users)
- **[Query Filters](./filters.md)** - How to filter aircraft queries by altitude, type, callsign, and more
- **[Advanced Usage](./advanced.md)** - Backend selection, low-level clients, error handling
- **[CLI Usage](./cli-usage.md)** - Command-line interface reference

### Developer Documentation

**For contributors and those extending the library:**

- **[Developer Documentation](./dev/README.md)** - Architecture, testing, contributing, and internal API details

## What's Inside

### High-Level Client (Recommended)

The `SkySnoop` unified client is the **recommended interface** for most applications:

- ✅ **Simple API** - One interface for all queries
- ✅ **Automatic backend selection** - Chooses the best backend automatically
- ✅ **Normalized responses** - Consistent data structure regardless of backend
- ✅ **Type-safe** - Full type hints and validation

[Learn more about the SkySnoop client →](./skysnoop-client.md)

### Low-Level Clients (Advanced)

For advanced use cases requiring direct backend access:

- **ReAPIClient** - Direct access to feeder-only RE-API backend
- **OpenAPIClient** - Direct access to public OpenAPI backend

[Learn more about advanced usage →](./advanced.md)

### Command-Line Interface

Query aircraft data from your terminal:

```bash
# Find aircraft by hex code
skysnoop hex 4CA87C

# Search within 50nm of San Francisco
skysnoop circle 37.7749 -122.4194 50

# Find closest aircraft
skysnoop closest 37.7749 -122.4194 100
```

[Learn more about CLI usage →](./cli-usage.md)

## About adsb.lol

[adsb.lol](https://adsb.lol) is a community-driven ADS-B aggregation service that collects aircraft position data from volunteers worldwide.

### API Backends

SkySnoop supports two adsb.lol API backends:

| Backend | URL | Access | Features |
|---------|-----|--------|----------|
| **RE-API** | `https://re-api.adsb.lol/` | Feeder-only | Full features, native operations |
| **OpenAPI** | `https://api.adsb.lol/` | Public | Identifier queries, simulated geographic queries |

The SkySnoop client automatically selects the appropriate backend and normalizes responses, so you typically don't need to worry about which backend is being used.

### Getting Feeder Access

To access the RE-API backend:

1. Visit [adsb.lol](https://adsb.lol) for setup instructions
2. Configure an ADS-B receiver to feed the network
3. Run queries from your feeder IP address

### Public Access

The OpenAPI backend is publicly accessible and doesn't require a feeder. API keys may be required in the future.

## Common Use Cases

### Find Aircraft Near a Location

```python
async with SkySnoop() as client:
    result = await client.get_in_circle(
        lat=37.7749,  # San Francisco
        lon=-122.4194,
        radius=50  # nautical miles
    )
    print(f"Found {result.result_count} aircraft")
```

### Track a Specific Aircraft

```python
async with SkySnoop() as client:
    # By ICAO hex code
    result = await client.get_by_hex("4CA87C")

    # By callsign
    result = await client.get_by_callsign("UAL123")

    # By registration
    result = await client.get_by_registration("N12345")
```

### Filter by Aircraft Type or Altitude

```python
from skysnoop.query.filters import QueryFilters

async with SkySnoop() as client:
    filters = QueryFilters(
        type_code="B738",  # Boeing 737-800
        above_alt_baro=30000,  # Above 30,000 feet
        below_alt_baro=40000   # Below 40,000 feet
    )

    result = await client.get_in_circle(
        lat=37.7749,
        lon=-122.4194,
        radius=100,
        filters=filters
    )
```

## Response Data

All queries return a `SkyData` object with normalized aircraft information:

```python
result = await client.get_by_hex("4CA87C")

# Metadata
print(f"Query timestamp: {result.timestamp}")
print(f"Aircraft count: {result.result_count}")
print(f"Backend used: {result.backend}")

# Aircraft data
for aircraft in result.aircraft:
    print(f"Hex: {aircraft.hex}")
    print(f"Flight: {aircraft.flight}")
    print(f"Position: {aircraft.lat}, {aircraft.lon}")
    print(f"Altitude: {aircraft.alt_baro} feet")
    print(f"Speed: {aircraft.gs} knots")
```

## Error Handling

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
        print("Operation not supported on this backend")
    except TimeoutError:
        print("Request timed out")
    except APIError as e:
        print(f"API error: {e}")
    except SkySnoopError as e:
        print(f"Error: {e}")
```

## Next Steps

- **New users**: Start with [Getting Started](./getting-started.md)
- **Quick reference**: See [SkySnoop Client Guide](./skysnoop-client.md)
- **Advanced features**: Check out [Advanced Usage](./advanced.md)
- **Command line**: See [CLI Usage](./cli-usage.md)
- **Contributing**: Read [Developer Documentation](./dev/README.md)

## Resources

- **GitHub Repository**: [github.com/tedivm/skysnoop](https://github.com/tedivm/skysnoop)
- **PyPI Package**: [pypi.org/project/skysnoop](https://pypi.org/project/skysnoop)
- **adsb.lol Main Site**: [adsb.lol](https://adsb.lol)
- **OpenAPI Documentation**: [api.adsb.lol/docs](https://api.adsb.lol/docs)

## Support

- **Issues**: [GitHub Issues](https://github.com/tedivm/skysnoop/issues)

## License

SkySnoop is released under the MIT License. See the [LICENSE](../LICENSE) file for details.
