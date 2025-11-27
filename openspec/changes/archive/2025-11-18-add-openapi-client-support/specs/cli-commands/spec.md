# cli-commands Specification Delta

## ADDED Requirements

### Requirement: OpenAPI Root Command

The system SHALL provide a root command for OpenAPI operations.

**Priority**: MUST
**Category**: CLI
**Rationale**: Organizes OpenAPI commands under a clear namespace separate from re-api commands.

#### Scenario: Display openapi command help

**Given** the adsblol CLI
**When** the command "adsblol openapi --help" is run
**Then** help text is displayed
**And** subcommands for v2 and v0 endpoints are listed
**And** usage examples are shown
**And** API key configuration is explained

#### Scenario: OpenAPI command without API key

**Given** the adsblol CLI
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

**Given** the adsblol CLI
**When** the command "adsblol openapi v2 pia" is run
**Then** aircraft with PIA addresses are fetched
**And** results are displayed in table format
**And** the --json flag outputs JSON format

#### Scenario: Query military aircraft

**Given** the adsblol CLI
**When** the command "adsblol openapi v2 mil" is run
**Then** military registered aircraft are fetched
**And** results are displayed in table format

#### Scenario: Query LADD aircraft

**Given** the adsblol CLI
**When** the command "adsblol openapi v2 ladd" is run
**Then** aircraft on LADD filter are fetched
**And** results are displayed in table format

#### Scenario: Query by squawk code

**Given** the adsblol CLI
**And** a squawk code (e.g., "7700")
**When** the command "adsblol openapi v2 squawk 7700" is run
**Then** aircraft with squawk 7700 are fetched
**And** results are displayed in table format

#### Scenario: Query by aircraft type

**Given** the adsblol CLI
**And** an aircraft type (e.g., "A320")
**When** the command "adsblol openapi v2 type A320" is run
**Then** aircraft of type A320 are fetched
**And** results are displayed in table format

#### Scenario: Query by registration

**Given** the adsblol CLI
**And** a registration (e.g., "G-KELS")
**When** the command "adsblol openapi v2 registration G-KELS" is run
**Then** aircraft with registration G-KELS are fetched
**And** results are displayed in table format

#### Scenario: Query by ICAO hex

**Given** the adsblol CLI
**And** an ICAO hex code (e.g., "4CA87C")
**When** the command "adsblol openapi v2 hex 4CA87C" is run
**Then** aircraft with hex 4CA87C are fetched
**And** results are displayed in table format

#### Scenario: Query by callsign

**Given** the adsblol CLI
**And** a callsign (e.g., "JBU1942")
**When** the command "adsblol openapi v2 callsign JBU1942" is run
**Then** aircraft with callsign JBU1942 are fetched
**And** results are displayed in table format

#### Scenario: Query by point and radius

**Given** the adsblol CLI
**And** coordinates and radius
**When** the command "adsblol openapi v2 point 37.7749 -122.4194 50" is run
**Then** aircraft within 50nm of the point are fetched
**And** results are displayed in table format

#### Scenario: Find closest aircraft

**Given** the adsblol CLI
**And** coordinates and radius
**When** the command "adsblol openapi v2 closest 37.7749 -122.4194 50" is run
**Then** the closest aircraft within 50nm is fetched
**And** result is displayed

---

### Requirement: OpenAPI V0 CLI Commands

The system SHALL provide CLI commands for OpenAPI v0 endpoints.

**Priority**: SHOULD
**Category**: CLI
**Rationale**: Provides access to auxiliary data from the command line.

#### Scenario: Query airport information

**Given** the adsblol CLI
**And** an airport ICAO code (e.g., "KJFK")
**When** the command "adsblol openapi v0 airport KJFK" is run
**Then** airport information is fetched
**And** results are displayed

#### Scenario: Get receiver information

**Given** the adsblol CLI
**When** the command "adsblol openapi v0 me" is run
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

**Given** ADSBLOL_API_KEY is set in environment
**When** any OpenAPI command is run
**Then** the API key from environment is used
**And** no --api-key flag is required

#### Scenario: Override with CLI flag

**Given** ADSBLOL_API_KEY is set in environment
**And** the --api-key flag is provided
**When** any OpenAPI command is run
**Then** the CLI flag value is used instead of environment
**And** the environment variable is ignored

#### Scenario: API key not displayed in help

**Given** the adsblol CLI
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

**Given** the adsblol CLI root help
**When** "adsblol --help" is run
**Then** both re-api and OpenAPI command groups are shown
**And** help text explains when to use each API
**And** differences between APIs are documented

---

## MODIFIED Requirements

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
