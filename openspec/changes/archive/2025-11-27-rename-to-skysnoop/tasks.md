# Implementation Tasks

## Phase 1: Setup and Validation

- [x] Create OpenSpec proposal structure
- [x] Validate proposal with `openspec validate rename-to-skysnoop --strict`
- [x] Ensure all tests pass before starting rename

## Phase 2: Core Rename (Preserve Git History)

- [x] Rename main package directory: `git mv adsblol skysnoop`
- [x] Update `pyproject.toml`:
  - Change `name = "adsblol"` to `name = "skysnoop"`
  - Update `[project.scripts]` from `adsblol` to `skysnoop`
  - Update any references in description or metadata

## Phase 3: Python Code Updates

**CRITICAL**: Do NOT use mass search/replace. Many legitimate references to "adsb.lol" must be preserved (API URLs, service references, documentation links). Review each file individually.

- [x] Update all import statements in `skysnoop/` package files (preserve API URLs and service references)
- [x] Update all import statements in `tests/` directory (preserve test data and service references)
- [x] Update string literals referencing package name (but NOT service URLs or documentation)
- [x] Update logger names (should use `__name__` so auto-updates)
- [x] Update exception messages if they reference package name
- [x] Verify API endpoint URLs remain unchanged (e.g., `https://api.adsb.lol`, `https://re-api.adsb.lol`)

## Phase 4: Documentation Updates

- [x] Update `README.md`:
  - Title and description
  - Installation instructions
  - All CLI examples
  - All Python import examples
  - Badges and links
- [x] Update all files in `docs/dev/`:
  - `architecture.md`
  - `cli.md`
  - `openapi-client.md`
  - `settings.md`
  - `testing.md`
  - Any other doc files
- [x] Update `AGENTS.md` if it contains package references

## Phase 5: OpenSpec Updates

- [x] Update `openspec/project.md`:
  - Project name and description
  - All path references
  - All code examples
- [x] Update spec files in `openspec/specs/`:
  - `api-client/spec.md`
  - `cli-commands/spec.md`
  - Any other affected specs

## Phase 6: Configuration and Metadata

- [x] Update `.github/` workflows if any reference the package name
- [x] Update `makefile` if it references package name
- [x] Verify `setuptools_scm` configuration works with renamed package

## Phase 7: Testing and Verification

- [x] Reinstall package in development mode: `pip install -e .`
- [x] Run full test suite: `make test` or `pytest`
- [x] Verify CLI works: `skysnoop --help`
- [x] Test import in Python: `python -c "from skysnoop.client import OpenAPIClient"`
- [x] Verify all documentation renders correctly
- [x] Run type checking: `mypy skysnoop/`
- [x] Run linting: `ruff check skysnoop/`

## Phase 8: Final Validation

- [x] Run `openspec validate --strict` on entire project
- [x] Review git diff to ensure no unintended changes
- [x] Verify git history preserved for package directory
- [ ] Create migration notes for users
- [ ] Tag version for release

## Notes

- **Preserve History**: Always use `git mv` for file/directory renames
- **Test Frequently**: Run tests after each phase to catch issues early
- **No Backward Compatibility**: This is a breaking change; clean break is intentional
- **NO Mass Replace**: Do NOT use automated search/replace on "adsblol" - legitimate service references must be preserved
- **Search Thoroughly**: Use `rg adsblol` to find references, but review each one individually
- **Service References**: Keep all references to "adsb.lol" the service (URLs, documentation, comments about the service)
