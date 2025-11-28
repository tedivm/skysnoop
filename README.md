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
- 🔌 **Dual API Support**: Both OpenAPI (public) and RE-API (feeder) clients

## API Access

This library provides **two API clients**:

### OpenAPI Client (Public API)

The **OpenAPI client** uses the public `https://api.adsb.lol` endpoint:

- ✅ **Publicly accessible** - no feeder requirement
- ✅ **Official OpenAPI spec** - auto-generated models
- ✅ **Type-safe** - full Pydantic v2 validation
- 🔑 API keys will be required in the future (currently unavailable)

See [OpenAPI Client Documentation](docs/dev/openapi-client.md) for details.

### RE-API Client (Feeder API)

The **RE-API client** uses the `https://re-api.adsb.lol/` endpoint:

- 🎯 **Feeder-only** - requires feeding data to adsb.lol network
- 📡 **Legacy API** - original implementation
- 🔓 No API key required, but must run from the Feeder IP address

**Getting Feeder Access:**

1. Set up an ADS-B receiver to feed data to adsb.lol
2. Visit the [adsb.lol documentation](https://adsb.lol/) for setup instructions
3. Join the adsb.lol community

**API Documentation:**

- OpenAPI Documentation: [https://api.adsb.lol/docs](https://api.adsb.lol/docs)
- OpenAPI Spec: [https://api.adsb.lol/api/openapi.json](https://api.adsb.lol/api/openapi.json)
- Main Site: [https://adsb.lol](https://adsb.lol)
- Community Support: Available through the adsb.lol platform

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

### OpenAPI Client (Recommended)

The OpenAPI client provides access to the public API with type-safe, validated responses.

#### CLI Usage

```bash
# Query military aircraft
skysnoop openapi v2 mil

# Find aircraft by ICAO hex
skysnoop openapi v2 hex 4CA87C

# Find aircraft near a point (within 50nm)
skysnoop openapi v2 point 37.7749 -- -122.4194 50

# Get closest aircraft
skysnoop openapi v2 closest 37.7749 -- -122.4194 100

# Output as JSON
skysnoop openapi v2 mil --json
```

#### Python Library Usage

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

        # Access aircraft data
        for aircraft in response.ac:
            print(f"{aircraft.hex}: {aircraft.flight} at {aircraft.alt_baro}ft")

asyncio.run(main())
```

See [OpenAPI Client Documentation](docs/dev/openapi-client.md) for full details.

### RE-API Client (Feeder-Only)

The RE-API client requires feeder access but provides additional functionality.

#### CLI Usage

Query aircraft within 50 nautical miles of San Francisco:

```bash
skysnoop circle -- 37.7749 -122.4194 50
```

Find all Airbus A321 aircraft:

```bash
skysnoop find-type A321
```

Get JSON output for programmatic use:

```bash
skysnoop circle --json -- 37.7749 -122.4194 50
```

Filter by altitude:

```bash
skysnoop circle --above-alt 30000 -- 37.7749 -122.4194 200
```

#### Python Library Usage

```python
import asyncio
from skysnoop.client.api import ReAPIClient

async def main():
    # Create client
    async with ReAPIClient() as client:
        # Query aircraft in a circular area
        response = await client.circle(
            lat=37.7749,
            lon=-122.4194,
            radius=50  # nautical miles
        )

        # Iterate through results
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

## CLI Commands

### Geographic Queries

- **`circle`** - Query aircraft within a radius of a point

  ```bash
  skysnoop circle -- <lat> <lon> <radius_nm>
  ```

- **`closest`** - Find the closest aircraft to a point

  ```bash
  skysnoop closest -- <lat> <lon> <max_radius_nm>
  ```

- **`box`** - Query aircraft within a bounding box

  ```bash
  skysnoop box -- <lat_south> <lat_north> <lon_west> <lon_east>
  ```

### Identifier Queries

- **`find-hex`** - Find aircraft by ICAO hex code

  ```bash
  skysnoop find-hex <hex_code>
  ```

- **`find-callsign`** - Find aircraft by callsign

  ```bash
  skysnoop find-callsign <callsign>
  ```

- **`find-reg`** - Find aircraft by registration

  ```bash
  skysnoop find-reg <registration>
  ```

- **`find-type`** - Find all aircraft of a specific type

  ```bash
  skysnoop find-type <type_code>
  ```

### Bulk Queries

- **`all-aircraft`** - Query all aircraft (with position by default)

  ```bash
  skysnoop all-aircraft
  skysnoop all-aircraft --include-no-position  # Include aircraft without position
  ```

### Common Options

All geographic and bulk commands support these filters:

- `--json` - Output as JSON instead of table
- `--callsign <callsign>` - Filter by exact callsign
- `--callsign-prefix <prefix>` - Filter by callsign prefix
- `--type <type>` - Filter by aircraft type (e.g., A321, B738)
- `--squawk <squawk>` - Filter by squawk code
- `--above-alt <feet>` - Filter for aircraft above altitude
- `--below-alt <feet>` - Filter for aircraft below altitude
- `--military` - Filter for military aircraft

**Note**: When using negative coordinates (e.g., longitude), use `--` before the coordinates to prevent them from being interpreted as options.

## API Reference

### ReAPIClient

Main client class for querying the adsb.lol API.

```python
from skysnoop.client.api import ReAPIClient

async with ReAPIClient(
    base_url="https://re-api.adsb.lol/",  # Default API URL
    timeout=30.0  # Request timeout in seconds
) as client:
    # Use client methods
    pass
```

#### Methods

##### Geographic Queries

- **`circle(lat, lon, radius, filters=None)`** - Query aircraft in circular area
  - Returns: `APIResponse`
  - Parameters:
    - `lat` (float): Latitude in decimal degrees
    - `lon` (float): Longitude in decimal degrees
    - `radius` (float): Radius in nautical miles
    - `filters` (QueryFilters, optional): Filter criteria

- **`closest(lat, lon, radius, filters=None)`** - Find closest aircraft
  - Returns: `APIResponse` (max 1 aircraft)

- **`box(lat_south, lat_north, lon_west, lon_east, filters=None)`** - Query bounding box
  - Returns: `APIResponse`

##### Identifier Queries

- **`find_hex(hex_code)`** - Find by ICAO 24-bit address
- **`find_callsign(callsign)`** - Find by callsign
- **`find_reg(registration)`** - Find by registration
- **`find_type(type_code)`** - Find by aircraft type

##### Bulk Queries

- **`all_with_pos(filters=None)`** - All aircraft with position data
- **`all(filters=None)`** - All aircraft including those without position

### QueryFilters

Filter criteria for queries.

```python
from skysnoop.query.filters import QueryFilters

filters = QueryFilters(
    callsign_exact="UAL123",        # Exact callsign match
    callsign_prefix="UAL",          # Callsign prefix (mutually exclusive with exact)
    type_code="A321",                # Aircraft type code
    squawk="7700",                   # Squawk code
    above_alt_baro=30000,            # Minimum altitude in feet
    below_alt_baro=40000,            # Maximum altitude in feet
    mil=True,                        # Military aircraft only
    pia=False,                       # Privacy/PIA flag
    ladd=False                       # LADD flag
)
```

### Aircraft Model

The `Aircraft` Pydantic model represents individual aircraft data.

**Key Fields:**

- `hex` (str, required): ICAO 24-bit address
- `flight` (str | None): Callsign/flight number
- `registration` (str | None): Aircraft registration
- `type` (str | None): Aircraft type code
- `lat` (float | None): Latitude
- `lon` (float | None): Longitude
- `alt_baro` (int | Literal["ground"] | None): Barometric altitude or "ground"
- `alt_geom` (int | Literal["ground"] | None): Geometric altitude or "ground"
- `gs` (float | None): Ground speed in knots
- `track` (float | None): Track angle in degrees
- `squawk` (str | None): Squawk code

**Properties:**

- `has_position` (bool): True if lat/lon are set
- `position_age` (float | None): Seconds since position updated
- `callsign` (str | None): Cleaned callsign (stripped whitespace)

### APIResponse Model

Response wrapper containing aircraft data.

```python
response = await client.circle(...)

print(response.resultCount)  # Number of aircraft
print(response.now)          # Query timestamp
print(response.ptime)        # Processing time

# Iterate aircraft
for aircraft in response:
    print(aircraft.hex)

# Direct access
aircraft_list = response.aircraft
```

## Error Handling

The library defines custom exceptions in `skysnoop.exceptions`:

```python
from skysnoop.exceptions import SkySnoopError, APIError, TimeoutError, ValidationError

try:
    async with ReAPIClient() as client:
        response = await client.circle(lat=37.7749, lon=-122.4194, radius=50)
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

**Note:** Live API tests require valid API credentials. You must be feeding data to adsb.lol to have API access. See the [API Access](#api-access) section above.

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

## About adsb.lol

[adsb.lol](https://adsb.lol) is a community-driven ADS-B aggregation service that collects aircraft position data from volunteers worldwide. API access is **free for feeders** who contribute data to the network.

**Resources:**

- **Main Site**: [https://adsb.lol](https://adsb.lol)
- **API Documentation**: [https://api.adsb.lol/docs](https://api.adsb.lol/docs)
- **Feeding Guide**: Check the adsb.lol site for instructions on setting up a feeder

**Important Notes:**

- Altitude can be an integer or the string "ground" for aircraft on the ground
- All distances are in nautical miles
- All altitudes are in feet
- All speeds are in knots
- API access requires feeding data to the adsb.lol network

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
