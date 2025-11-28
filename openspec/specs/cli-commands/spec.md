# cli-commands Specification

## Purpose

TBD - created by archiving change add-core-sdk-client. Update Purpose after archive.

## Requirements

### Requirement: Circle Query Command

The system SHALL provide a CLI command to query aircraft within a circular area.

**Priority**: MUST
**Category**: CLI
**Rationale**: Most common spatial query for finding nearby aircraft.

#### Scenario: Query aircraft in circle

**Given** the CLI is invoked with "skysnoop circle 37.7749 -122.4194 200"
**When** the command executes
**Then** aircraft within 200 nautical miles of the coordinates are retrieved
**And** the results are displayed in a human-readable format

#### Scenario: Circle query with filters

**Given** the CLI is invoked with "skysnoop circle 37.7749 -122.4194 200 --type A321"
**When** the command executes
**Then** only A321 aircraft within the circle are retrieved
**And** the results are displayed

#### Scenario: Circle query with JSON output

**Given** the CLI is invoked with "skysnoop circle 37.7749 -122.4194 200 --json"
**When** the command executes
**Then** results are output as JSON
**And** the JSON is valid and parseable

---

### Requirement: Closest Aircraft Command

The system SHALL provide a CLI command to find the closest aircraft to a location.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Useful for finding the nearest aircraft to a specific point.

#### Scenario: Find closest aircraft

**Given** the CLI is invoked with "skysnoop closest 37.7749 -122.4194 500"
**When** the command executes
**Then** the single closest aircraft within 500 NM is retrieved
**And** the result is displayed with distance information

#### Scenario: No aircraft found

**Given** the CLI is invoked with closest command and a remote location
**When** the command executes and no aircraft are in range
**Then** a message indicating no aircraft found is displayed
**And** the command exits with success status

---

### Requirement: Bounding Box Query Command

The system SHALL provide a CLI command to query aircraft within a rectangular bounding box.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Enables rectangular area searches for region-based queries.

#### Scenario: Query aircraft in box

**Given** the CLI is invoked with "skysnoop box 37.7 -122.5 37.8 -122.3"
**When** the command executes
**Then** aircraft within the specified box are retrieved
**And** the results are displayed

---

### Requirement: Find by Hex Command

The system SHALL provide a CLI command to lookup aircraft by ICAO hex identifier.

**Priority**: MUST
**Category**: CLI
**Rationale**: Direct aircraft lookup is a core use case.

#### Scenario: Find aircraft by hex

**Given** the CLI is invoked with "skysnoop find-hex abc123"
**When** the command executes
**Then** the aircraft with hex "abc123" is retrieved
**And** all available telemetry is displayed

#### Scenario: Hex not found

**Given** the CLI is invoked with a hex that doesn't exist
**When** the command executes
**Then** a message indicating aircraft not found is displayed
**And** the command exits with success status

---

### Requirement: Find by Callsign Command

The system SHALL provide a CLI command to lookup aircraft by flight callsign.

**Priority**: MUST
**Category**: CLI
**Rationale**: Users often want to track specific flights by callsign.

#### Scenario: Find aircraft by callsign

**Given** the CLI is invoked with "skysnoop find-callsign UAL123"
**When** the command executes
**Then** aircraft with callsign "UAL123" are retrieved
**And** the results are displayed

#### Scenario: Multiple aircraft with same callsign

**Given** multiple aircraft have the same callsign
**When** the find-callsign command is executed
**Then** all matching aircraft are displayed

---

### Requirement: Find by Registration Command

The system SHALL provide a CLI command to lookup aircraft by registration number.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Aircraft registration is a unique identifier users may want to search by.

#### Scenario: Find aircraft by registration

**Given** the CLI is invoked with "skysnoop find-reg N12345"
**When** the command executes
**Then** the aircraft with registration "N12345" is retrieved
**And** the results are displayed

---

### Requirement: Find by Type Command

The system SHALL provide a CLI command to find all aircraft of a specific type.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Users may want to track all aircraft of a particular model.

#### Scenario: Find aircraft by type

**Given** the CLI is invoked with "skysnoop find-type A321"
**When** the command executes
**Then** all A321 aircraft are retrieved
**And** the results are displayed

---

### Requirement: List All Aircraft Command

The system SHALL provide a CLI command to retrieve all tracked aircraft.

**Priority**: MUST
**Category**: CLI
**Rationale**: Provides complete visibility into all tracked aircraft.

#### Scenario: List all aircraft with positions

**Given** the CLI is invoked with "skysnoop all"
**When** the command executes
**Then** all aircraft with position data are retrieved
**And** the results are displayed

#### Scenario: List all aircraft including those without positions

**Given** the CLI is invoked with "skysnoop all --include-no-position"
**When** the command executes
**Then** all aircraft (with or without positions) are retrieved
**And** the results are displayed

---

### Requirement: Output Formatting

The system SHALL provide consistent output formatting for aircraft data across all command types.

**Changes**: Extended to support OpenAPI v2 response format in addition to re-api format.

**Priority**: MUST
**Category**: CLI
**Rationale**: Ensures consistent user experience across both API types.

#### Scenario: Format re-api response as table

**Given** an APIResponse from re-api
**When** format_table() is called
**Then** a Rich table is returned
**And** columns include hex, callsign, altitude, position, etc.
**And** the table displays all aircraft

#### Scenario: Format OpenAPI v2 response as table

**Given** a V2Response_Model from OpenAPI
**When** format_table() is called
**Then** a Rich table is returned
**And** columns match OpenAPI field names where applicable
**And** the table displays all aircraft
**And** formatting is consistent with re-api output

#### Scenario: Format re-api response as JSON

**Given** an APIResponse from re-api
**When** format_json() is called
**Then** JSON string is returned
**And** the JSON is properly formatted and indented
**And** all data is preserved

#### Scenario: Format OpenAPI v2 response as JSON

**Given** a V2Response_Model from OpenAPI
**When** format_json() is called
**Then** JSON string is returned
**And** the JSON is properly formatted and indented
**And** all data is preserved

### Requirement: Common Filter Options

The system SHALL provide common filter options as CLI flags for all query commands.

**Priority**: MUST
**Category**: CLI
**Rationale**: Users need to filter results without writing code.

#### Scenario: Filter by altitude

**Given** a query command with "--above-alt 30000" flag
**When** the command executes
**Then** only aircraft above 30000 feet are included in results

#### Scenario: Filter by aircraft type

**Given** a query command with "--type A321" flag
**When** the command executes
**Then** only A321 aircraft are included in results

#### Scenario: Filter by callsign prefix

**Given** a query command with "--callsign-prefix UAL" flag
**When** the command executes
**Then** only aircraft with callsigns starting with "UAL" are included

#### Scenario: Combine multiple filters

**Given** a query command with multiple filter flags
**When** the command executes
**Then** aircraft matching all filter criteria are returned

---

### Requirement: Error Handling and User Messages

The system SHALL provide clear, user-friendly error messages for CLI commands.

**Priority**: MUST
**Category**: CLI
**Rationale**: Users need to understand what went wrong and how to fix it.

#### Scenario: Network error

**Given** the API is unreachable
**When** any query command is executed
**Then** a clear error message about network connectivity is displayed
**And** the command exits with non-zero status

#### Scenario: Invalid coordinates

**Given** a query command with out-of-range latitude or longitude
**When** the command executes
**Then** an error message explaining valid coordinate ranges is displayed
**And** the command exits with non-zero status

#### Scenario: Timeout error

**Given** a query that times out
**When** the command executes
**Then** a clear timeout error message is displayed
**And** suggestions for increasing timeout are provided

#### Scenario: No results found

**Given** a query that returns zero aircraft
**When** the command completes
**Then** a message indicating no aircraft found is displayed
**And** the command exits with success status (this is not an error)

---

### Requirement: Configuration via Settings

The system SHALL allow CLI behavior to be configured via settings file or environment variables.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Users need to customize default behavior without command-line flags.

#### Scenario: Configure API endpoint

**Given** ADSB_API_BASE_URL is set in environment
**When** any CLI command is executed
**Then** the custom API endpoint is used for requests

#### Scenario: Configure default timeout

**Given** ADSB_API_TIMEOUT is set in environment
**When** any CLI command is executed
**Then** the custom timeout value is used

#### Scenario: Configure default output format

**Given** CLI_OUTPUT_FORMAT is set in settings
**When** any query command is executed without format flag
**Then** the configured output format is used

---

### Requirement: Help and Documentation

The system SHALL provide comprehensive help text for all CLI commands and options.

**Priority**: MUST
**Category**: CLI
**Rationale**: Users need to discover and understand available commands.

#### Scenario: Display main help

**Given** the CLI is invoked with "--help"
**When** the command executes
**Then** a list of all available commands is displayed
**And** brief descriptions of each command are shown

#### Scenario: Display command-specific help

**Given** the CLI is invoked with "skysnoop circle --help"
**When** the command executes
**Then** detailed help for the circle command is displayed
**And** all parameters and options are documented
**And** usage examples are provided

#### Scenario: Display version information

**Given** the CLI is invoked with "--version"
**When** the command executes
**Then** the current version of skysnoop is displayed

---

### Requirement: Progress Indicators

The system SHALL display progress indicators for long-running queries.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Users need feedback during queries that may take several seconds.

#### Scenario: Show spinner during query

**Given** a CLI query command is executing
**And** the query takes more than 1 second
**When** waiting for results
**Then** a spinner or progress indicator is displayed
**And** the indicator disappears when results are ready

#### Scenario: No progress indicator for fast queries

**Given** a CLI query command is executing
**And** results return in less than 1 second
**When** the command completes
**Then** no progress indicator is shown

---

### Requirement: Result Limiting

The system SHALL provide options to limit the number of results displayed.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Queries may return many results; users need to limit output.

#### Scenario: Limit number of results

**Given** a query command with "--limit 10" flag
**When** the command executes and returns 50 aircraft
**Then** only the first 10 aircraft are displayed

#### Scenario: Display result count

**Given** any query command
**When** the command completes
**Then** the total number of aircraft found is displayed
**And** if limited, both shown and total counts are displayed

### Requirement: OpenAPI Root Command

The system SHALL provide a root command for OpenAPI operations.

**Priority**: MUST
**Category**: CLI
**Rationale**: Organizes OpenAPI commands under a clear namespace separate from re-api commands.

#### Scenario: Display openapi command help

**Given** the skysnoop CLI
**When** the command "skysnoop openapi --help" is run
**Then** help text is displayed
**And** subcommands for v2 and v0 endpoints are listed
**And** usage examples are shown
**And** API key configuration is explained

#### Scenario: OpenAPI command without API key

**Given** the skysnoop CLI
**And** no API key is configured
**When** an OpenAPI command is run
**Then** the command proceeds normally (API keys not required yet)
**And** no warning is displayed

---

### Requirement: OpenAPI V2 CLI Commands

The system SHALL provide CLI commands for all OpenAPI v2 endpoints.

**Priority**: MUST
**Category**: CLI
**Rationale**: Allows users to query the OpenAPI from the command line.

#### Scenario: Query PIA aircraft

**Given** the skysnoop CLI
**When** the command "skysnoop openapi v2 pia" is run
**Then** aircraft with PIA addresses are fetched
**And** results are displayed in table format
**And** the --json flag outputs JSON format

#### Scenario: Query military aircraft

**Given** the skysnoop CLI
**When** the command "skysnoop openapi v2 mil" is run
**Then** military registered aircraft are fetched
**And** results are displayed in table format

#### Scenario: Query LADD aircraft

**Given** the skysnoop CLI
**When** the command "skysnoop openapi v2 ladd" is run
**Then** aircraft on LADD filter are fetched
**And** results are displayed in table format

#### Scenario: Query by squawk code

**Given** the skysnoop CLI
**And** a squawk code (e.g., "7700")
**When** the command "skysnoop openapi v2 squawk 7700" is run
**Then** aircraft with squawk 7700 are fetched
**And** results are displayed in table format

#### Scenario: Query by aircraft type

**Given** the skysnoop CLI
**And** an aircraft type (e.g., "A320")
**When** the command "skysnoop openapi v2 type A320" is run
**Then** aircraft of type A320 are fetched
**And** results are displayed in table format

#### Scenario: Query by registration

**Given** the skysnoop CLI
**And** a registration (e.g., "G-KELS")
**When** the command "skysnoop openapi v2 registration G-KELS" is run
**Then** aircraft with registration G-KELS are fetched
**And** results are displayed in table format

#### Scenario: Query by ICAO hex

**Given** the skysnoop CLI
**And** an ICAO hex code (e.g., "4CA87C")
**When** the command "skysnoop openapi v2 hex 4CA87C" is run
**Then** aircraft with hex 4CA87C are fetched
**And** results are displayed in table format

#### Scenario: Query by callsign

**Given** the skysnoop CLI
**And** a callsign (e.g., "JBU1942")
**When** the command "skysnoop openapi v2 callsign JBU1942" is run
**Then** aircraft with callsign JBU1942 are fetched
**And** results are displayed in table format

#### Scenario: Query by point and radius

**Given** the skysnoop CLI
**And** coordinates and radius
**When** the command "skysnoop openapi v2 point 37.7749 -122.4194 50" is run
**Then** aircraft within 50nm of the point are fetched
**And** results are displayed in table format

#### Scenario: Find closest aircraft

**Given** the skysnoop CLI
**And** coordinates and radius
**When** the command "skysnoop openapi v2 closest 37.7749 -122.4194 50" is run
**Then** the closest aircraft within 50nm is fetched
**And** result is displayed

---

### Requirement: OpenAPI V0 CLI Commands

The system SHALL provide CLI commands for OpenAPI v0 endpoints.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Provides access to auxiliary data from the command line.

#### Scenario: Query airport information

**Given** the skysnoop CLI
**And** an airport ICAO code (e.g., "KJFK")
**When** the command "skysnoop openapi v0 airport KJFK" is run
**Then** airport information is fetched
**And** results are displayed

#### Scenario: Get receiver information

**Given** the skysnoop CLI
**When** the command "skysnoop openapi v0 me" is run
**Then** receiver and global stats are fetched
**And** results are displayed in readable format

---

### Requirement: OpenAPI Output Formatting

The system SHALL format OpenAPI command output consistently with existing commands.

**Priority**: MUST
**Category**: CLI
**Rationale**: Provides consistent user experience across all CLI commands.

#### Scenario: Default table output

**Given** any OpenAPI CLI command
**When** run without --json flag
**Then** results are formatted as a Rich table
**And** key fields are included in columns
**And** the table is colored and styled consistently
**And** the result count is shown

#### Scenario: JSON output format

**Given** any OpenAPI CLI command
**When** run with --json flag
**Then** raw JSON response is printed
**And** JSON is formatted with indentation
**And** output is valid JSON that can be piped to other tools

#### Scenario: Empty results handling

**Given** any OpenAPI CLI command
**And** the query returns no results
**When** the command completes
**Then** a message "No aircraft found" is displayed
**And** the exit code is 0 (success)

#### Scenario: Error display

**Given** any OpenAPI CLI command
**And** an error occurs (network, validation, etc.)
**When** the command runs
**Then** the error message is displayed in red
**And** the error type is clear
**And** the exit code is non-zero

---

### Requirement: CLI Configuration for API Key

The system SHALL support API key configuration via CLI flag and environment variable.

**Priority**: MUST
**Category**: CLI
**Rationale**: Allows users to specify API key without hardcoding.

#### Scenario: Use environment variable for API key

**Given** SKYSNOOP_API_KEY is set in environment
**When** any OpenAPI command is run
**Then** the API key from environment is used
**And** no --api-key flag is required

#### Scenario: Override with CLI flag

**Given** SKYSNOOP_API_KEY is set in environment
**And** the --api-key flag is provided
**When** any OpenAPI command is run
**Then** the CLI flag value is used instead of environment
**And** the environment variable is ignored

#### Scenario: API key not displayed in help

**Given** the skysnoop CLI
**When** --help is displayed for OpenAPI commands
**Then** API key values are not shown
**And** help text explains key configuration

---

### Requirement: CLI Help and Examples

The system SHALL provide comprehensive help text and examples for OpenAPI commands.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Improves discoverability and reduces learning curve.

#### Scenario: Command help includes examples

**Given** any OpenAPI CLI command
**When** --help is requested
**Then** usage examples are shown
**And** parameter descriptions are clear
**And** expected output format is explained

#### Scenario: Root help explains API choice

**Given** the skysnoop CLI root help
**When** "skysnoop --help" is run
**Then** both re-api and OpenAPI command groups are shown
**And** help text explains when to use each API
**And** differences between APIs are documented

---

