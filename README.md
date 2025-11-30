# skysnoop

A Python SDK and CLI for querying aircraft data from [adsb.lol](https://adsb.lol), a community-driven ADS-B aggregation service.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🛩️ **Comprehensive API Coverage**: Query aircraft by location, identifier, type, and more
- 🎯 **Type-Safe**: Full type hints and Pydantic models for all data structures
- ⚡ **Async-First**: Built on httpx for high-performance async operations
- 🖥️ **Beautiful CLI**: Rich terminal output with tables and JSON formatting
- 🔍 **Flexible Filtering**: Filter by altitude, type, callsign, squawk, and more
- 🧪 **Well-Tested**: >90% code coverage with comprehensive test suite
- 🔌 **Dual Backend Support**: Works with both OpenAPI (public) and RE-API (feeder) backends

## Documentation

**Complete documentation is available at [docs/README.md](./docs/README.md)**

- **[Getting Started](./docs/getting-started.md)** - Installation and basic usage
- **[SkySnoop Client Guide](./docs/skysnoop-client.md)** - Complete API reference
- **[Query Filters](./docs/filters.md)** - Filtering aircraft by altitude, type, etc.
- **[Advanced Usage](./docs/advanced.md)** - Backend selection, low-level clients, optimization
- **[CLI Usage](./docs/cli-usage.md)** - Command-line interface guide

**For Contributors:**

- **[Developer Documentation](./docs/dev/README.md)** - Architecture, testing, and contributing

## About adsb.lol

[adsb.lol](https://adsb.lol) is a community-driven ADS-B aggregation service that collects aircraft position data from volunteers worldwide.

**API Backends:**

- **RE-API** - Feeder-only API with full features
- **OpenAPI** - Public API (some features simulated)

The **SkySnoop unified client** automatically handles both backends, selecting the appropriate one and normalizing responses.

**Resources:**

- **Main Site**: [https://adsb.lol](https://adsb.lol)
- **OpenAPI Docs**: [https://api.adsb.lol/docs](https://api.adsb.lol/docs)

## Installation

### From PyPI

```bash
pip install skysnoop
```

### From Source

```bash
git clone https://github.com/tedivm/skysnoop.git
cd skysnoop
pip install -e .
```

## Quick Start

### High-Level Client (Recommended)

The **SkySnoop unified client** provides a single, consistent interface that works with both API backends. It automatically selects the appropriate backend, normalizes responses, and handles differences transparently.

**Key Benefits:**

- ✅ **Single interface** - no need to learn two different APIs
- ✅ **Automatic backend selection** - uses RE-API by default, OpenAPI as fallback
- ✅ **Normalized responses** - consistent data structure regardless of backend
- ✅ **Future-proof** - ready for API key authentication when available
- ✅ **Flexible** - can explicitly choose backend when needed

#### Python Usage

```python
import asyncio
from skysnoop import SkySnoop

async def main():
    # Auto-select backend (recommended - prefers RE-API, falls back to OpenAPI)
    async with SkySnoop() as client:
        # Query by ICAO hex
        result = await client.get_by_hex("4CA87C")
        print(f"Found {result.result_count} aircraft")

        # Query aircraft in a circle (50nm radius)
        result = await client.get_in_circle(
            lat=37.7749,
            lon=-122.4194,
            radius=50
        )

        # Get closest aircraft within 100nm
        result = await client.get_closest(
            lat=37.7749,
            lon=-122.4194,
            radius=100
        )

        # Access aircraft data
        for aircraft in result.aircraft:
            print(f"{aircraft.hex}: {aircraft.flight} at {aircraft.alt_baro}ft")

asyncio.run(main())
```

With filters:

```python
from skysnoop import SkySnoop
from skysnoop.query.filters import QueryFilters

async def main():
    async with SkySnoop() as client:
        # Create filters
        filters = QueryFilters(
            above_alt_baro=30000,
            type_code="A321",
            military=True
        )

        # Query with filters
        result = await client.get_in_circle(
            lat=37.7749,
            lon=-122.4194,
            radius=200,
            filters=filters
        )

        print(f"Found {result.result_count} military A321s above 30,000ft")

asyncio.run(main())
```

Explicit backend selection:

```python
async def main():
    # Force RE-API backend (feeder access required)
    async with SkySnoop(backend="reapi") as client:
        result = await client.get_in_box(
            lat_min=37.0,
            lat_max=38.0,
            lon_min=-123.0,
            lon_max=-122.0
        )

    # Force OpenAPI backend (public access)
    async with SkySnoop(backend="openapi") as client:
        result = await client.get_by_hex("4CA87C")

asyncio.run(main())
```

### Backend Comparison

| Feature | RE-API | OpenAPI | SkySnoop (auto) |
|---------|--------|---------|-----------------|
| **Access** | Feeder-only | Public | Auto-selects |
| **`get_by_hex()`** | ✅ | ✅ | ✅ |
| **`get_by_callsign()`** | ✅ | ✅ | ✅ |
| **`get_by_registration()`** | ✅ | ✅ | ✅ |
| **`get_by_type()`** | ✅ | ✅ | ✅ |
| **`get_in_circle()`** | ✅ Native | ✅ Simulated* | ✅ |
| **`get_closest()`** | ✅ Native | ✅ Simulated* | ✅ |
| **`get_in_box()`** | ✅ Native | ✅ Simulated* | ✅ |
| **`get_all_with_pos()`** | ✅ | ❌ | ⚠️ Backend-dependent |
| **Filters** | ✅ Full support | ⚠️ Limited** | ⚠️ Backend-dependent |
| **API Key** | Not required | Future | Optional |

\* OpenAPI simulates geographic queries by fetching all aircraft and filtering client-side
\** OpenAPI supports only `military` filter via separate endpoint

---

### Low-Level Clients (Advanced Use)

For advanced use cases requiring direct backend access, you can use the low-level client implementations:

#### OpenAPI Client

Direct access to the public OpenAPI backend with versioned endpoints and type-safe generated models.

```python
import asyncio
from skysnoop.client import OpenAPIClient

async def main():
    async with OpenAPIClient() as client:
        # Query by ICAO hex
        response = await client.v2.get_by_hex(icao_hex="4CA87C")

        # Query military aircraft
        response = await client.v2.get_mil()

        # Query by location
        response = await client.v2.get_by_point(
            lat=37.7749,
            lon=-122.4194,
            radius=50
        )

        # Access aircraft data (note: uses .ac instead of .aircraft)
        for aircraft in response.ac:
            print(f"{aircraft.hex}: {aircraft.flight} at {aircraft.alt_baro}ft")

asyncio.run(main())
```

See [OpenAPI Client Documentation](docs/dev/openapi-client.md) for full details.

#### RE-API Client

Direct access to the feeder-only RE-API backend with native support for all geographic queries.

```python
import asyncio
from skysnoop.client.api import ReAPIClient

async def main():
    async with ReAPIClient() as client:
        # Query aircraft in a circular area
        response = await client.circle(
            lat=37.7749,
            lon=-122.4194,
            radius=50  # nautical miles
        )

        # Iterate through results (note: uses .resultCount instead of .result_count)
        print(f"Found {response.resultCount} aircraft")
        for aircraft in response:
            print(f"{aircraft.hex}: {aircraft.flight} at {aircraft.alt_baro}ft")

asyncio.run(main())
```

With filters:

```python
from skysnoop.query.filters import QueryFilters

async def main():
    async with ReAPIClient() as client:
        # Create filters
        filters = QueryFilters(
            above_alt_baro=30000,
            type_code="A321"
        )

        # Query with filters
        response = await client.circle(
            lat=37.7749,
            lon=-122.4194,
            radius=200,
            filters=filters
        )

        for aircraft in response:
            print(f"{aircraft.hex}: {aircraft.type} at {aircraft.alt_baro}ft")

asyncio.run(main())
```

**Note**: The low-level clients have different APIs and response formats. Consider using the SkySnoop unified client for a consistent interface.

## CLI Usage

The `skysnoop` CLI provides a convenient command-line interface for querying aircraft data.

### Backend Selection

All commands support the `--backend` option to choose which API backend to use:

```bash
# Auto-select backend (default - prefers RE-API, falls back to OpenAPI)
skysnoop circle --backend auto -- 37.7749 -122.4194 50

# Force RE-API backend (feeder access required)
skysnoop circle --backend reapi -- 37.7749 -122.4194 50

# Force OpenAPI backend (public access)
skysnoop find-hex --backend openapi 4CA87C
```

**Note:** The default backend is `auto`, which automatically selects RE-API (feeder) or OpenAPI (public) based on availability.

### Geographic Queries

Query aircraft by location:

```bash
# Query aircraft within a radius of a point
skysnoop circle -- <lat> <lon> <radius_nm>
skysnoop circle -- 37.7749 -122.4194 50

# Find the closest aircraft to a point
skysnoop closest -- <lat> <lon> <max_radius_nm>
skysnoop closest -- 37.7749 -122.4194 100

# Query aircraft within a bounding box
skysnoop box -- <lat_south> <lat_north> <lon_west> <lon_east>
skysnoop box -- 37.0 38.0 -123.0 -122.0
```

### Identifier Queries

Query aircraft by identifier:

```bash
# Find aircraft by ICAO hex code
skysnoop find-hex <hex_code>
skysnoop find-hex 4CA87C

# Find aircraft by callsign
skysnoop find-callsign <callsign>
skysnoop find-callsign UAL123

# Find aircraft by registration
skysnoop find-reg <registration>
skysnoop find-reg N12345

# Find all aircraft of a specific type
skysnoop find-type <type_code>
skysnoop find-type A321
```

### Bulk Queries

Query all aircraft:

```bash
# Query all aircraft with position data
skysnoop all-aircraft

# Include aircraft without position data
skysnoop all-aircraft --include-no-position
```

### Filtering Options

All commands support filtering options:

- `--backend <auto|reapi|openapi>` - Choose API backend
- `--json` - Output as JSON instead of table
- `--callsign <callsign>` - Filter by exact callsign
- `--callsign-prefix <prefix>` - Filter by callsign prefix
- `--type <type>` - Filter by aircraft type (e.g., A321, B738)
- `--squawk <squawk>` - Filter by squawk code
- `--above-alt <feet>` - Filter for aircraft above altitude
- `--below-alt <feet>` - Filter for aircraft below altitude
- `--military` - Filter for military aircraft

**Examples:**

```bash
# Military aircraft above 30,000ft with auto backend selection
skysnoop circle --backend auto --military --above-alt 30000 -- 37.7749 -122.4194 200

# A321 aircraft with JSON output
skysnoop find-type --json A321

# Aircraft with callsign prefix using OpenAPI backend
skysnoop circle --backend openapi --callsign-prefix UAL -- 37.7749 -122.4194 100
```

### Low-Level CLI Commands

For direct access to backend-specific features:

```bash
# OpenAPI v2 endpoints
skysnoop openapi v2 mil              # Query military aircraft
skysnoop openapi v2 hex 4CA87C       # Find by hex
skysnoop openapi v2 point 37.7749 -- -122.4194 50  # Query by location
skysnoop openapi v2 closest 37.7749 -- -122.4194 100  # Closest aircraft
```

**Note**: When using negative coordinates (e.g., longitude), use `--` before the coordinates to prevent them from being interpreted as options.

## Error Handling

The library defines custom exceptions in `skysnoop.exceptions`:

```python
from skysnoop import SkySnoop
from skysnoop.exceptions import (
    SkySnoopError,
    APIError,
    TimeoutError,
    ValidationError,
    UnsupportedOperationError
)

try:
    async with SkySnoop() as client:
        result = await client.get_in_circle(lat=37.7749, lon=-122.4194, radius=50)
        for aircraft in result.aircraft:
            print(f"{aircraft.hex}: {aircraft.callsign}")
except UnsupportedOperationError as e:
    print(f"Operation not supported by backend: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except APIError as e:
    print(f"API error: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except SkySnoopError as e:
    print(f"General error: {e}")
```

### Exception Hierarchy

- `SkySnoopError` - Base exception for all library errors
  - `APIError` - HTTP/API errors (4xx, 5xx responses)
  - `ValidationError` - Invalid parameters or data
  - `TimeoutError` - Request timeout
  - `UnsupportedOperationError` - Operation not supported by the selected backend

You can catch all library errors with the base exception:

```python
from skysnoop import SkySnoop
from skysnoop.exceptions import SkySnoopError

try:
    async with SkySnoop() as client:
        result = await client.get_in_circle(lat=37.7749, lon=-122.4194, radius=50)
        for aircraft in result.aircraft:
            print(f"{aircraft.hex}: {aircraft.callsign}")
except SkySnoopError as e:
    # Catches all library-specific errors
    print(f"SkySnoop error: {e}")
```

## Configuration

Configure the library via environment variables or settings:

```python
from skysnoop.settings import settings

# Settings can be overridden
settings.adsb_api_base_url = "https://re-api.adsb.lol/"
settings.adsb_api_timeout = 30.0
settings.cli_output_format = "table"  # or "json"
```

Or via environment variables:

```bash
export ADSB_API_BASE_URL="https://re-api.adsb.lol/"
export ADSB_API_TIMEOUT="30.0"
export CLI_OUTPUT_FORMAT="table"
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/tedivm/skysnoop.git
cd skysnoop
make install
```

This will create a virtual environment at `.venv` and install all development dependencies.

### Run Tests

```bash
# Run all tests with coverage
make pytest

# Run specific test with verbose output
make pytest_loud

# Run live API tests (requires API access from adsb.lol)
make pytest_live
```

**Note:** Live API tests require API access. For the OpenAPI access this is currently open to all with no API key, but may be restricted in the future. For the RE-API you must be feeding data to adsb.lol to have API access. See the [About adsb.lol](#about-adsblol) section above.

### Code Quality

```bash
# Run all quality checks (tests + linting + type checking)
make tests

# Format code
make black_fixes

# Lint code
make ruff_check

# Type checking
make mypy_check

# Auto-fix linting issues
make ruff_fixes

# Run all formatting fixes
make chores
```

## Data Format Notes

**Important conventions:**

- **Altitude**: Can be an integer (in feet) or the string `"ground"` for aircraft on the ground
- **Distances**: All distances are in nautical miles
- **Altitudes**: All altitudes are in feet
- **Speeds**: All speeds are in knots
- **Coordinates**: Latitude/longitude in decimal degrees

## Documentation

For complete documentation, see:

- **[User Documentation](./docs/README.md)** - Getting started, API reference, CLI usage
- **[Developer Documentation](./docs/dev/README.md)** - Architecture, contributing, testing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Data from [adsb.lol](adsb.lol) is available under the [ODbl license](https://www.adsb.lol/docs/open-data/api/).
