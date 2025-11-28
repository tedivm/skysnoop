# cli-commands Spec Delta

## MODIFIED Requirements

### Requirement: CLI Command Name and Entry Point

The CLI command name SHALL be changed from `adsblol` to `skysnoop`.

**Priority**: MUST
**Category**: CLI
**Rationale**: Project rename requires updating the CLI command to match the new package name and brand.

#### Scenario: Invoke CLI with new command name

**Given** the skysnoop package is installed
**When** a user runs `skysnoop --help`
**Then** the CLI help text is displayed
**And** all commands are accessible via `skysnoop`
**And** the command functions identically to the previous `adsblol` command

#### Scenario: Circle query with new command

**Given** the skysnoop CLI is installed
**When** the CLI is invoked with `skysnoop circle 37.7749 -122.4194 200`
**Then** aircraft within 200 nautical miles of the coordinates are retrieved
**And** the results are displayed in a human-readable format

#### Scenario: OpenAPI commands with new command

**Given** the skysnoop CLI is installed
**When** the CLI is invoked with `skysnoop openapi v2 mil`
**Then** military aircraft are retrieved via the OpenAPI endpoint
**And** the results are displayed

#### Scenario: Old command name no longer works

**Given** the skysnoop package is installed (and adsblol is uninstalled)
**When** a user runs `adsblol --help`
**Then** the command is not found
**And** an appropriate shell error is displayed

### Requirement: CLI Examples in Help Text

All CLI help text and examples SHALL reference the `skysnoop` command.

**Priority**: MUST
**Category**: CLI
**Rationale**: User-facing documentation must be consistent with the actual command name.

#### Scenario: Help text shows correct command

**Given** a user runs `skysnoop --help`
**When** the help text is displayed
**Then** all examples use `skysnoop` as the command name
**And** no references to `adsblol` appear in the help text

## MODIFIED Requirements (Documentation)

### Requirement: CLI Documentation Updates

All CLI documentation SHALL be updated to reference the `skysnoop` command.

**Priority**: MUST
**Category**: Documentation
**Rationale**: Users rely on documentation for learning and reference.

#### Scenario: README examples use new command

**Given** a user reads the README
**When** reviewing CLI examples
**Then** all command examples use `skysnoop`
**And** all import examples use `from skysnoop import ...`
**And** no references to `adsblol` remain

#### Scenario: Developer documentation uses new command

**Given** a user reads the developer documentation
**When** reviewing CLI development examples
**Then** all examples use the `skysnoop` command and package name
**And** configuration paths reference `skysnoop/`

## Implementation Notes

- Update `pyproject.toml` `[project.scripts]` section: `skysnoop = "skysnoop.cli:app"`
- All CLI example strings in code and docs must change from `adsblol` to `skysnoop`
- Help text should reflect the new command name
- No alias or backward compatibility provided for the old `adsblol` command
