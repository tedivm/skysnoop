"""Script to capture real API responses for test fixtures.

This script queries the live adsb.lol API and saves responses as JSON files
for use in testing. It requires access to the adsb.lol API (feeder IP or VPN).

Run this script when you have API access to capture/update test fixtures.
"""

import asyncio
import json
from pathlib import Path

import httpx

# Base URL for the API
BASE_URL = "https://re-api.adsb.lol/"

# Output directory for fixtures
FIXTURES_DIR = Path(__file__).parent / "api_responses"


async def capture_response(client: httpx.AsyncClient, query: str, filename: str, description: str):
    """Capture an API response and save it to a file.

    Args:
        client: HTTP client to use for the request
        query: Query string for the API (e.g., "circle=52,2,200")
        filename: Name of the output JSON file
        description: Human-readable description of the query
    """
    print(f"Capturing {description}...")
    try:
        url = f"{BASE_URL}?{query}"
        response = await client.get(url, timeout=30.0)
        if response.status_code != 200:
            print(f"  ✗ HTTP {response.status_code}: {response.text[:200]}")
            return

        data = response.json()

        # Save to file
        output_path = FIXTURES_DIR / filename
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        result_count = data.get("resultCount", len(data.get("aircraft", [])))
        print(f"  ✓ Saved {result_count} aircraft to {filename}")

    except httpx.HTTPError as e:
        print(f"  ✗ Error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")


async def main():
    """Capture all API responses for test fixtures."""
    print("Starting API response capture...")
    print(f"Output directory: {FIXTURES_DIR}")
    print()

    async with httpx.AsyncClient() as client:
        # Circle queries - San Francisco area
        await capture_response(
            client,
            "circle=37.7749,-122.4194,200",
            "circle_multiple_aircraft.json",
            "circle query with multiple aircraft (SF, 200nm radius)",
        )

        await capture_response(
            client,
            "circle=37.7749,-122.4194,10",
            "circle_single_aircraft.json",
            "circle query with single/few aircraft (SF, 10nm radius)",
        )

        # Small radius, remote area - likely zero results
        await capture_response(
            client,
            "circle=60.0,-145.0,5",
            "circle_zero_results.json",
            "circle query with zero results (remote Alaska, 5nm radius)",
        )

        # Closest query
        await capture_response(
            client,
            "closest=37.7749,-122.4194,200",
            "closest_response.json",
            "closest query (SF, 200nm radius)",
        )

        # Box query (format: lat_south,lat_north,lon_west,lon_east)
        await capture_response(
            client,
            "box=37.0,38.5,-123.0,-121.0",
            "box_response.json",
            "box query (SF Bay Area)",
        )

        # Find hex - we'll use a real hex from the circle query
        await capture_response(
            client,
            "find_hex=a4a4e8",
            "find_hex_success.json",
            "find hex query (real hex from SF area)",
        )

        # Find callsign
        await capture_response(
            client,
            "find_callsign=ASA",
            "find_callsign_multiple.json",
            "find callsign query (Alaska Airlines prefix)",
        )

        # Find registration
        await capture_response(
            client,
            "find_reg=N399HA",
            "find_reg_response.json",
            "find registration query (specific aircraft)",
        )

        # Find type
        await capture_response(
            client,
            "find_type=A332",
            "find_type_response.json",
            "find type query (A330-200)",
        )

        # All with position
        await capture_response(
            client,
            "all_with_pos",
            "all_with_pos_sample.json",
            "all query with positions",
        )

    print()
    print("Capture complete!")
    print(f"Fixtures saved to: {FIXTURES_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
