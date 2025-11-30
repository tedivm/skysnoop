# CLI Usage Guide

SkySnoop includes a powerful command-line interface for querying aircraft data directly from your terminal.

## Installation

The CLI is included when you install SkySnoop:

```bash
pip install skysnoop
```

Verify installation:

```bash
skysnoop --version
```

## Quick Start

```bash
# Find aircraft by hex code
skysnoop hex 4CA87C

# Search near San Francisco (50nm radius)
skysnoop circle 37.7749 -122.4194 50

# Find closest aircraft
skysnoop closest 37.7749 -122.4194 100

# Get output as JSON
skysnoop hex 4CA87C --output json
```

## Basic Commands

### skysnoop hex

Find aircraft by ICAO hex code.

```bash
skysnoop hex 4CA87C
skysnoop hex abc123
```

**Options**:

- `--output`, `-o`: Output format (`table` or `json`)
- `--backend`, `-b`: Backend selection (`auto`, `reapi`, `openapi`)

### skysnoop callsign

Find aircraft by callsign/flight number.

```bash
skysnoop callsign UAL123
skysnoop callsign "UNITED 123"
```

### skysnoop registration

Find aircraft by registration (tail number).

```bash
skysnoop registration N12345
skysnoop registration G-ABCD
```

### skysnoop type

Find aircraft by type designator.

```bash
skysnoop type B738
skysnoop type A320
```

## Geographic Commands

### skysnoop circle

Find aircraft within a circular area.

```bash
# Syntax: skysnoop circle <lat> <lon> <radius>
skysnoop circle 37.7749 -122.4194 50

# With filters
skysnoop circle 37.7749 -122.4194 100 --military

# JSON output
skysnoop circle 37.7749 -122.4194 50 --output json
```

**Parameters**:

- `lat`: Center latitude (decimal degrees)
- `lon`: Center longitude (decimal degrees)
- `radius`: Search radius (nautical miles)

**Options**:

- `--callsign-exact`: Filter by exact callsign
- `--callsign-prefix`: Filter by callsign prefix
- `--type`: Filter by aircraft type
- `--squawk`: Filter by squawk code
- `--above-alt`: Filter above altitude (feet)
- `--below-alt`: Filter below altitude (feet)
- `--military`: Show only military aircraft
- `--interesting`: Show only interesting aircraft

### skysnoop closest

Find the closest aircraft to a point.

```bash
# Syntax: skysnoop closest <lat> <lon> <radius>
skysnoop closest 37.7749 -122.4194 100

# With filters
skysnoop closest 40.6413 -73.7781 50 --type B738
```

**Parameters**: Same as `circle`

**Options**: Same filtering options as `circle`

### skysnoop box

Find aircraft in a rectangular bounding box.

```bash
# Syntax: skysnoop box <lat-min> <lat-max> <lon-min> <lon-max>
skysnoop box 37.0 38.0 -123.0 -122.0

# With filters
skysnoop box 37.0 38.0 -123.0 -122.0 --above-alt 30000
```

**Parameters**:

- `lat-min`: Southern boundary
- `lat-max`: Northern boundary
- `lon-min`: Western boundary
- `lon-max`: Eastern boundary

**Options**: Same filtering options as `circle`

## Bulk Commands

### skysnoop all

Get all tracked aircraft (RE-API only).

```bash
skysnoop all

# With filters
skysnoop all --military --above-alt 10000

# Force RE-API backend
skysnoop all --backend reapi
```

**Note**: Only available with RE-API backend (feeder access required).

### skysnoop all-with-pos

Get all aircraft with position data (RE-API only).

```bash
skysnoop all-with-pos

# With filters
skysnoop all-with-pos --type B738
```

## Output Formats

### Table Format (Default)

```bash
skysnoop hex 4CA87C

# Output:
# ┏━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
# ┃ Hex    ┃ Flight  ┃ Registration ┃ Altitude ┃
# ┣━━━━━━━━╋━━━━━━━━━╋━━━━━━━━━━━━━━╋━━━━━━━━━━┫
# ┃ 4CA87C ┃ UAL123  ┃ N12345       ┃ 35000    ┃
# ┗━━━━━━━━┻━━━━━━━━━┻━━━━━━━━━━━━━━┻━━━━━━━━━━┛
```

Specify explicitly:

```bash
skysnoop hex 4CA87C --output table
```

### JSON Format

```bash
skysnoop hex 4CA87C --output json

# Output:
# {
#   "result_count": 1,
#   "backend": "reapi",
#   "timestamp": 1234567890.0,
#   "aircraft": [
#     {
#       "hex": "4CA87C",
#       "flight": "UAL123",
#       "registration": "N12345",
#       "lat": 37.7749,
#       "lon": -122.4194,
#       "alt_baro": 35000
#     }
#   ]
# }
```

## Filtering Options

All geographic and bulk commands support filters (RE-API only):

### Callsign Filters

```bash
# Exact callsign match
skysnoop circle 37.7749 -122.4194 50 --callsign-exact UAL123

# Callsign prefix
skysnoop circle 37.7749 -122.4194 50 --callsign-prefix UAL
```

### Type Filter

```bash
# Boeing 737-800s only
skysnoop circle 37.7749 -122.4194 100 --type B738
```

### Altitude Filters

```bash
# Above 30,000 feet
skysnoop circle 37.7749 -122.4194 100 --above-alt 30000

# Below 10,000 feet
skysnoop circle 37.7749 -122.4194 50 --below-alt 10000

# Altitude range (between 10,000 and 30,000 feet)
skysnoop circle 37.7749 -122.4194 100 --above-alt 10000 --below-alt 30000
```

### Special Category Filters

```bash
# Military aircraft only
skysnoop circle 37.7749 -122.4194 100 --military

# Interesting aircraft only
skysnoop circle 37.7749 -122.4194 100 --interesting
```

### Squawk Code Filter

```bash
# Emergency squawk
skysnoop circle 37.7749 -122.4194 100 --squawk 7700

# VFR squawk (US)
skysnoop circle 37.7749 -122.4194 50 --squawk 1200
```

### Combining Filters

```bash
# United Airlines flights above 30,000 feet
skysnoop circle 37.7749 -122.4194 100 \
  --callsign-prefix UAL \
  --above-alt 30000

# Military aircraft below 10,000 feet (departing/arriving)
skysnoop circle 38.8503 -77.0369 25 \
  --military \
  --below-alt 10000

# Boeing 737-800s cruising altitude
skysnoop all-with-pos \
  --type B738 \
  --above-alt 30000 \
  --below-alt 42000
```

## Backend Selection

### Automatic (Default)

```bash
# Automatically selects best backend
skysnoop hex 4CA87C
```

### Force RE-API

```bash
skysnoop hex 4CA87C --backend reapi
```

**Note**: Requires feeder access.

### Force OpenAPI

```bash
skysnoop hex 4CA87C --backend openapi
```

**Note**: Publicly accessible.

## Global Options

These options work with all commands:

```bash
# Output format
skysnoop hex 4CA87C --output json
skysnoop hex 4CA87C -o json

# Backend selection
skysnoop hex 4CA87C --backend reapi
skysnoop hex 4CA87C -b openapi

# Help
skysnoop --help
skysnoop hex --help
skysnoop circle --help
```

## OpenAPI Specific Commands

When using OpenAPI backend (explicitly or via auto-selection), additional commands are available:

### skysnoop openapi mil

Get military aircraft.

```bash
skysnoop openapi mil
skysnoop openapi mil --output json
```

### skysnoop openapi pia

Get privacy-flagged aircraft.

```bash
skysnoop openapi pia
```

### skysnoop openapi ladd

Get LADD-protected aircraft.

```bash
skysnoop openapi ladd
```

### skysnoop openapi squawk

Find aircraft by squawk code.

```bash
skysnoop openapi squawk 7700
skysnoop openapi squawk 1200
```

## Common Use Cases

### Monitor Specific Airport

```bash
# Aircraft within 25nm of SFO
skysnoop circle 37.6213 -122.3790 25

# Departures (climbing below 10,000ft)
skysnoop circle 37.6213 -122.3790 25 \
  --above-alt 100 \
  --below-alt 10000
```

### Track Airline Fleet

```bash
# All United Airlines flights
skysnoop all-with-pos --callsign-prefix UAL

# United flights near JFK
skysnoop circle 40.6413 -73.7781 100 \
  --callsign-prefix UAL
```

### Find Specific Aircraft Type

```bash
# All A380s currently flying
skysnoop all-with-pos --type A388

# A380s near London
skysnoop circle 51.4700 -0.4543 100 --type A388
```

### Emergency Aircraft

```bash
# Aircraft declaring emergency
skysnoop all-with-pos --squawk 7700
```

### Military Activity

```bash
# Military aircraft in area
skysnoop circle 38.8503 -77.0369 50 --military

# All military aircraft with position
skysnoop all-with-pos --military
```

## Piping and Scripting

### Save to File

```bash
# Save JSON output
skysnoop hex 4CA87C --output json > aircraft.json

# Save table output
skysnoop circle 37.7749 -122.4194 50 > aircraft.txt
```

### Pipe to jq

```bash
# Extract hex codes
skysnoop circle 37.7749 -122.4194 50 --output json | \
  jq -r '.aircraft[].hex'

# Filter by altitude in jq
skysnoop all-with-pos --output json | \
  jq '.aircraft[] | select(.alt_baro > 30000)'

# Count aircraft by type
skysnoop circle 37.7749 -122.4194 100 --output json | \
  jq '.aircraft | group_by(.type) | map({type: .[0].type, count: length})'
```

### Periodic Monitoring

```bash
# Monitor every 60 seconds
while true; do
  skysnoop circle 37.7749 -122.4194 50
  sleep 60
done

# Save with timestamps
while true; do
  echo "=== $(date) ==="
  skysnoop circle 37.7749 -122.4194 50
  sleep 60
done | tee monitoring.log
```

## Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Quick airport monitoring
alias sfo-aircraft='skysnoop circle 37.6213 -122.3790 25'
alias jfk-aircraft='skysnoop circle 40.6413 -73.7781 25'
alias lax-aircraft='skysnoop circle 33.9416 -118.4085 25'

# Emergency monitoring
alias emergencies='skysnoop all-with-pos --squawk 7700'

# Military tracking
alias military='skysnoop all-with-pos --military'

# JSON output
alias skysnoop-json='skysnoop --output json'
```

## Environment Variables

Configure CLI defaults:

```bash
# Backend selection
export SKYSNOOP_BACKEND="reapi"

# API key (future)
export SKYSNOOP_API_KEY="your-api-key"

# Custom URLs
export ADSB_API_BASE_URL="https://custom.api.url"

# Output format
export SKYSNOOP_OUTPUT_FORMAT="json"
```

## Troubleshooting

### Command Not Found

```bash
skysnoop: command not found
```

**Solution**: Ensure pip bin directory is in PATH:

```bash
# Check installation
pip show skysnoop

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Permission Denied

```bash
skysnoop hex 4CA87C
# Permission denied
```

**Solution**: Install with --user flag:

```bash
pip install --user skysnoop
```

### No Results

If queries return no results:

1. Check coordinates are valid
2. Increase search radius
3. Try different backend: `--backend openapi`
4. Verify aircraft is currently airborne

### Timeout Errors

```bash
# Increase timeout (not yet implemented in CLI)
# Use Python API for custom timeouts
```

## Tips and Tricks

### Quick Reference Card

```bash
# Create quick reference
cat > ~/skysnoop-quick.txt << 'EOF'
# SkySnoop Quick Reference
skysnoop hex <code>              # By hex code
skysnoop callsign <cs>           # By callsign
skysnoop registration <reg>      # By registration
skysnoop circle <lat> <lon> <r>  # In circle
skysnoop closest <lat> <lon> <r> # Closest
skysnoop box <s> <n> <w> <e>     # In box
skysnoop all-with-pos            # All with position

# Filters (add to geographic/bulk commands)
--type B738                      # Aircraft type
--above-alt 30000                # Above altitude
--below-alt 10000                # Below altitude
--military                       # Military only
--callsign-prefix UAL            # Callsign prefix
--squawk 7700                    # Squawk code

# Output
--output json                    # JSON format
--output table                   # Table format (default)
--backend reapi                  # Force RE-API
--backend openapi                # Force OpenAPI
EOF

# View reference
cat ~/skysnoop-quick.txt
```

### Watch Mode

```bash
# Monitor with watch command
watch -n 30 'skysnoop circle 37.7749 -122.4194 50'
```

## Next Steps

- **Python API**: [SkySnoop Client Guide](./skysnoop-client.md)
- **Filters**: [Query Filters Guide](./filters.md)
- **Advanced usage**: [Advanced Usage Guide](./advanced.md)
- **Development**: [CLI Development Guide](./dev/cli.md) (for contributors)
