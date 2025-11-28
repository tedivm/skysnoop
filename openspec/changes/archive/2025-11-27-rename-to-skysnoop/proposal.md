# Proposal: Rename Project to skysnoop

## Context

The current project name `adsblol` is derived from the adsb.lol service. However, this project is an independent SDK and CLI, not owned by the adsb.lol service operators. Using their namespace could be confusing and potentially problematic. A rename is needed to establish a clear, independent identity.

## Motivation

- **Namespace Concerns**: `adsblol` closely mirrors the service name (adsb.lol), which could create confusion about ownership and maintenance responsibility
- **Independent Identity**: The SDK should have its own brand that reflects its purpose while being clearly separate from the service it consumes
- **Better Discoverability**: `skysnoop` is descriptive, memorable, and clearly indicates what the tool does (snooping/monitoring the sky for aircraft)
- **PyPI Availability**: `skysnoop` is available on PyPI and has a fun, punny quality that fits the aviation domain

## Proposed Change

Rename the project from `adsblol` to `skysnoop` across all components:

1. **Package Name**: `adsblol` → `skysnoop`
2. **Python Module**: `adsblol/` → `skysnoop/`
3. **CLI Command**: `adsblol` → `skysnoop`
4. **Repository Name**: (if applicable) `adsblol` → `skysnoop`
5. **Documentation**: Update all references in README, docs, and examples
6. **Import Statements**: Update all Python imports throughout the codebase

### Scope

This is a **breaking change** that affects:

- All users who import the library
- All users who use the CLI
- All documentation and examples
- PyPI package distribution

**No backward compatibility** will be maintained as this is a complete rebrand.

## Impact Analysis

### User Impact

- **Breaking**: All existing imports will break (`from adsblol import ...` → `from skysnoop import ...`)
- **Breaking**: CLI command changes (`adsblol` → `skysnoop`)
- **Migration Path**: Users must update their code and scripts after upgrade
- **Communication**: Release notes must clearly communicate the breaking change

### Code Impact

- Python package directory rename (use `git mv` to preserve history)
- ~100+ references across Python files, tests, and documentation
- PyPI package name change
- GitHub repository name change (optional but recommended)

### Maintenance Impact

- **Positive**: Clearer independent identity
- **Positive**: Better alignment with project purpose
- **Neutral**: One-time rename effort

## Implementation Strategy

1. **Use git mv**: Preserve git history for the package directory
2. **Selective Updates**: Carefully update package/module references while preserving legitimate references to the adsb.lol service
3. **Version Bump**: Release as a new major version (e.g., 1.0.0 or 2.0.0)
4. **Clear Communication**: Provide migration guide in release notes
5. **Verification**: Run full test suite to ensure functionality is preserved

### Critical Implementation Note

**Mass search/replace is NOT appropriate** for this rename. The codebase contains legitimate references to "adsb.lol" as a service that must be preserved:

- API endpoint URLs (e.g., `https://api.adsb.lol`, `https://re-api.adsb.lol`)
- Service documentation links
- Comments explaining that this SDK connects to the adsb.lol service
- References in docstrings about what the service provides

**What MUST change**:

- Package name: `adsblol` → `skysnoop`
- Python module directory: `adsblol/` → `skysnoop/`
- Import statements: `from adsblol` → `from skysnoop`
- CLI command: `adsblol` → `skysnoop`
- Package metadata and documentation examples

**What MUST NOT change**:

- API endpoint URLs containing "adsb.lol"
- Documentation explaining this connects to "adsb.lol"
- Comments like "Query the adsb.lol API"
- Links to <https://adsb.lol>

Each file must be reviewed individually to ensure service references remain intact.

## Alternatives Considered

1. **Keep current name**: Not viable due to namespace concerns
2. **Gradual migration with deprecation**: Overly complex for a name change; clean break is clearer
3. **Other names considered**: whatsup (taken), planely, planespy, etc. - `skysnoop` was chosen for its clarity and fun factor

## Success Criteria

- [ ] All code references updated
- [ ] All tests passing
- [ ] Documentation updated and accurate
- [ ] PyPI package published under new name
- [ ] Clear migration guide provided
- [ ] Git history preserved for main package directory
