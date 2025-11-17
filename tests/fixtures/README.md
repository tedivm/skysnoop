# Test Fixtures

This directory contains real API response data captured from the adsb.lol API for use in testing.

## Why Real API Data?

All mock data for tests MUST come from real API responses. This ensures:

1. **Realistic Testing**: Tests use actual data structures and edge cases from the live API
2. **CI/CD Compatibility**: Tests can run in environments (like GitHub Actions) where the API is not accessible due to IP restrictions
3. **Data Accuracy**: Response parsing and validation matches real-world API behavior
4. **Stability**: Tests don't depend on API availability or network conditions

## Capturing Fixtures

To capture or update fixtures:

1. **Ensure API Access**: You must have access to the adsb.lol API:
   - Feed data to adsb.lol (your IP will be whitelisted)
   - Use a VPN with an authorized IP
   - Contact adsb.lol for temporary API access

2. **Install Dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run Capture Script**:

   ```bash
   python tests/fixtures/capture_fixtures.py
   ```

4. **Review Captured Data**: Check that responses contain expected data and handle edge cases

## Fixture Files

### api_responses/

Contains raw JSON responses from the adsb.lol API:

- `circle_multiple_aircraft.json` - Circle query returning multiple aircraft
- `circle_single_aircraft.json` - Circle query returning one aircraft
- `circle_zero_results.json` - Circle query with no results
- `closest_response.json` - Closest aircraft query
- `box_response.json` - Box/rectangle area query
- `find_hex_success.json` - Find by hex code (success case)
- `find_callsign_multiple.json` - Find by callsign with multiple results
- `find_reg_response.json` - Find by registration
- `find_type_response.json` - Find by aircraft type
- `all_with_pos_sample.json` - All aircraft with positions (sample)
- `all_response.json` - All aircraft query (can be large)

## Query Parameters Used

Each fixture was captured with specific query parameters:

| File | Query Parameters | Description |
|------|-----------------|-------------|
| `circle_multiple_aircraft.json` | `circle=37.7749,-122.4194,200` | San Francisco, 200nm radius |
| `circle_single_aircraft.json` | `circle=37.7749,-122.4194,10` | San Francisco, 10nm radius |
| `circle_zero_results.json` | `circle=60.0,-145.0,5` | Remote Alaska, 5nm radius |
| `closest_response.json` | `closest=37.7749,-122.4194,200` | Closest to San Francisco |
| `box_response.json` | `box=37.0,-123.0,38.5,-121.0` | SF Bay Area rectangle |
| `find_hex_success.json` | `findHex=a12345` | Example hex code |
| `find_callsign_multiple.json` | `findCallsign=UAL` | United Airlines prefix |
| `find_reg_response.json` | `findReg=N` | N-registration prefix |
| `find_type_response.json` | `findType=B77` | Boeing 777 variants |
| `all_with_pos_sample.json` | `all=1` | All with positions |
| `all_response.json` | `all=` | All aircraft |

## Maintenance

Fixtures should be updated when:

- The adsb.lol API response format changes
- New fields are added to the API
- Edge cases are discovered that aren't covered by existing fixtures
- Test coverage requires additional scenarios

## Last Updated

Fixtures created: 2025-11-16 (Initial implementation)

Update this date when re-capturing fixtures.
