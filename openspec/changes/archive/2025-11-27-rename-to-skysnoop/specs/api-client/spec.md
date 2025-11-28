# api-client Spec Delta

## MODIFIED Requirements

### Requirement: Package and Module References

The API client package and module names SHALL be updated from `adsblol` to `skysnoop`.

**Priority**: MUST
**Category**: API Client
**Rationale**: Project rename requires updating all package references to maintain consistency and correct imports.

#### Scenario: Import OpenAPI client with new package name

**Given** the skysnoop package is installed
**When** a user imports the OpenAPI client
**Then** the import statement is `from skysnoop.client import OpenAPIClient`
**And** the import succeeds
**And** the client functions identically to the previous implementation

#### Scenario: Import RE-API client with new package name

**Given** the skysnoop package is installed
**When** a user imports the RE-API client
**Then** the import statement is `from skysnoop.client.api import ReAPIClient`
**And** the import succeeds
**And** the client functions identically to the previous implementation

**Note**: The `ReAPIClient` class name is intentionally preserved to minimize breaking changes. Only the package/module namespace changes to `skysnoop`.

#### Scenario: Import models with new package name

**Given** the skysnoop package is installed
**When** a user imports data models
**Then** import statements use the `skysnoop.models` namespace
**And** all model imports succeed
**And** models function identically to the previous implementation

#### Scenario: Internal imports reference skysnoop

**Given** the package has been renamed
**When** internal modules import from other package modules
**Then** all internal imports use `skysnoop` as the base package name
**And** no references to `adsblol` remain in import statements
**And** the package loads successfully

## Implementation Notes

- All Python files in the package must update their import statements
- The `ReAPIClient` class name remains unchanged (only namespace changes)
- Internal cross-module imports must use the new `skysnoop` package name
- Test files must update their imports to reference `skysnoop`
- No backward compatibility is provided for `adsblol` imports
