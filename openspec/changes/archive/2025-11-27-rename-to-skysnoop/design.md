# Design: Project Rename Strategy

## Overview

This design document outlines the technical approach for renaming the `adsblol` project to `skysnoop` while preserving git history and ensuring all functionality remains intact.

## Design Principles

1. **Preserve Git History**: Use `git mv` for all file and directory moves to maintain commit history
2. **Atomic Updates**: Group related changes together to minimize intermediate broken states
3. **Comprehensive Search**: Use both grep/ripgrep and IDE search to find all references
4. **Test-Driven Validation**: Run tests after each major phase to catch issues early
5. **Clean Break**: No backward compatibility - this is a complete rebrand

## Technical Decisions

### Package Directory Rename

**Decision**: Use `git mv adsblol skysnoop` to rename the package directory

**Rationale**:

- Preserves complete git history for all files in the package
- Git automatically tracks the rename in the commit
- Avoids losing blame/log information
- Standard practice for repository reorganization

**Alternative Considered**: Delete and recreate

- **Rejected**: Would lose all git history and blame information

### Import Statement Updates

**Decision**: Update all imports in a single commit after directory rename

**Rationale**:

- Ensures package is consistently named across codebase
- Easier to review as a single logical change
- Tests will immediately show what's broken

**Pattern**:

```python
# Old
from adsblol.client import OpenAPIClient
import adsblol.models.aircraft

# New
from skysnoop.client import OpenAPIClient
import skysnoop.models.aircraft
```

### CLI Command Rename

**Decision**: Change `[project.scripts]` in `pyproject.toml` from `adsblol` to `skysnoop`

**Rationale**:

- Single source of truth for CLI entrypoint
- Setuptools handles the command installation automatically
- No code changes needed in CLI implementation

**Impact**: Users must reinstall package for new command to be available

### PyPI Package Name

**Decision**: Publish under new name `skysnoop` without maintaining old name

**Rationale**:

- Clean break is clearer for users than gradual migration
- Avoids maintaining two package names
- `skysnoop` is available on PyPI

**Migration Path**:

- Users uninstall `adsblol` and install `skysnoop`
- Clear communication in release notes
- Consider leaving final `adsblol` version with deprecation notice pointing to `skysnoop`

### Version Numbering

**Decision**: Bump to next major version (e.g., if currently 0.x.x, go to 1.0.0)

**Rationale**:

- Breaking change deserves major version bump
- Signals significant change to users
- Follows semantic versioning principles

### Search Strategy

**CRITICAL**: Mass search/replace is NOT appropriate for this rename.

**Why Manual Review is Required**:

The codebase contains two distinct types of "adsblol" references:

1. **Package references** (must change): Import paths, CLI commands, package metadata
2. **Service references** (must preserve): API URLs, documentation about the adsb.lol service, links

**Search Tools**:

1. `rg adsblol` - Find all references for manual review
2. `grep -r "adsblol"` - Backup search method
3. IDE search - Handles case variations and context

**Review Process**:

- Use search tools to locate references
- Review EACH match individually
- Update package/module references
- Preserve service references (URLs, documentation)

**Examples of What to Preserve**:

- `https://api.adsb.lol` and `https://re-api.adsb.lol` (API endpoints)
- "connects to the adsb.lol service" (service description)
- `https://adsb.lol` (service homepage)
- Comments like "Query aircraft data from adsb.lol"

**Examples of What to Change**:

- `from adsblol.client import` → `from skysnoop.client import`
- `pip install adsblol` → `pip install skysnoop`
- `adsblol circle` → `skysnoop circle`
- Package name in `pyproject.toml`

**Scope**:

- Python files (`.py`)
- Configuration files (`.toml`, `.yaml`, `.json`)
- Documentation (`.md`, `.rst`)
- Scripts and makefiles
- GitHub workflows

### Testing Strategy

**Approach**: Test after each phase

**Key Tests**:

1. **Import Tests**: Verify all imports work with new name
2. **CLI Tests**: Verify command works with new name
3. **Unit Tests**: Full test suite must pass
4. **Integration Tests**: API calls work correctly
5. **Type Checking**: Mypy passes
6. **Linting**: Ruff passes

**Test Execution**:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Verify CLI
skysnoop --help
skysnoop openapi v2 mil --help

# Type checking
mypy skysnoop/

# Linting
ruff check skysnoop/
```

## File-by-File Changes

### Core Files

| File | Change Type | Details |
|------|-------------|---------|
| `adsblol/` → `skysnoop/` | Directory rename | Use `git mv` |
| `pyproject.toml` | Content update | Package name, scripts |
| `README.md` | Content update | All examples, imports, CLI commands |
| `AGENTS.md` | Content update | Package references |
| `openspec/project.md` | Content update | Project name, paths, examples |

### Python Files

All `.py` files need import statement updates:

- `skysnoop/**/*.py` - Internal imports
- `tests/**/*.py` - Test imports

### Documentation Files

All `.md` files in `docs/dev/` need updates:

- CLI command examples
- Import statements
- Configuration paths

### OpenSpec Files

Spec files need class and requirement name updates:

- `openspec/specs/api-client/spec.md` - Class names (ReAPIClient → SkysnoopClient or keep as is with note)
- `openspec/specs/cli-commands/spec.md` - Command examples

**Note**: Class names like `ReAPIClient` could remain unchanged in initial release for minimal disruption, or be renamed to `SkysnoopClient` for consistency.

## Class Naming Decision

**Decision**: Keep `ReAPIClient` class name unchanged initially

**Rationale**:

- Reduces scope of breaking changes
- Package/module name is the primary identifier
- Class can be aliased or renamed in future version
- Focuses this change on namespace/branding

**Alternative**: Rename to `SkysnoopClient`

- **Deferred**: Can be done in separate change if desired

## Risk Mitigation

### Risk: Missing References

**Mitigation**:

- Use multiple search tools
- Review git diff carefully
- Run comprehensive test suite
- Check documentation builds

### Risk: Broken Imports

**Mitigation**:

- Test suite will catch import errors
- Use Python import checking tools
- Install and test in clean environment

### Risk: Git History Loss

**Mitigation**:

- Always use `git mv` for renames
- Verify history with `git log --follow`
- Test before and after merge

## Rollout Plan

1. **Development**: Complete rename in feature branch
2. **Testing**: Extensive testing in development environment
3. **Review**: Code review with focus on completeness
4. **Documentation**: Update release notes with migration guide
5. **Release**: Publish to PyPI under new name
6. **Communication**: Announce change in release notes and README
7. **Archive**: (Optional) Leave stub version of `adsblol` pointing to `skysnoop`

## Success Metrics

- [ ] Zero import errors
- [ ] 100% test pass rate
- [ ] All documentation builds successfully
- [ ] CLI works correctly
- [ ] Git history preserved (verify with `git log --follow`)
- [ ] Type checking passes
- [ ] Linting passes
