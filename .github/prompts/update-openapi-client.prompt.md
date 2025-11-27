# Update OpenAPI Client

This prompt guides you through updating the adsblol OpenAPI client when the adsb.lol OpenAPI specification changes.

## Prerequisites

- OpenSpec change proposal exists: `add-openapi-client-support`
- GitHub issue created by spec monitoring workflow indicating spec has changed
- You have reviewed the issue for context

## Steps

### 1. Download and Compare Specifications

First, download the latest OpenAPI specification and compare it with the current version:

```bash
# Download latest spec
make openapi-download

# Compare with stored spec (if exists)
git diff resources/openapi_spec.json
```

Review the diff carefully and note:

- New endpoints added
- Removed endpoints
- Changed request/response schemas
- New required fields
- Deprecated fields

### 2. Identify Breaking Changes

Review the specification changes and identify breaking changes:

**Breaking Changes Include**:

- Removed endpoints
- Changed response structure (removed fields, type changes)
- New required request parameters
- Changed parameter types
- Changed authentication requirements

**Non-Breaking Changes Include**:

- New endpoints
- New optional fields in responses
- Additional optional parameters
- Documentation updates

Document all breaking changes in your response to the user.

### 3. Regenerate Models

Regenerate Pydantic models from the new specification:

```bash
make openapi-generate
```

Review the generated models:

- Check `adsblol/models/openapi/v2.py` for changes
- Check `adsblol/models/openapi/v0.py` for changes
- Look for new models, removed models, changed field types
- Ensure all models inherit from `pydantic.BaseModel`
- Verify field names match API exactly (no unwanted transformations)

### 4. Update Version Tracking

Update the version tracking module:

1. Open `adsblol/client/openapi_version.py`
2. Update `OPENAPI_VERSION` from the spec `info.version`
3. Update `SPEC_HASH` by calculating SHA256 of spec file
4. Update `SPEC_UPDATED` to current date (YYYY-MM-DD format)

### 5. Update Client Methods

Review `adsblol/client/openapi.py` and update as needed:

**For New Endpoints**:

- Add new methods to appropriate class (V2Methods or V0Methods)
- Follow existing method pattern:
  - Async method
  - Type hints for all parameters and return values
  - Docstring with description, parameters, return type, and example
  - Error handling
- Use generated models for response parsing

**For Changed Endpoints**:

- Update method signatures if parameters changed
- Update return type if response model changed
- Update docstrings to reflect changes
- Add deprecation warnings if endpoint will be removed

**For Removed Endpoints**:

- Mark method as deprecated with clear message
- Raise `DeprecationWarning` when called
- Document alternative endpoint/method to use
- Plan removal in future major version

### 6. Update CLI Commands

Review `adsblol/cli.py` and update OpenAPI commands:

**For New Endpoints**:

- Add new CLI command under appropriate group (v2/v0)
- Follow Typer patterns used by existing commands
- Add `--json` flag support
- Add comprehensive help text with examples
- Use appropriate output formatter

**For Changed Endpoints**:

- Update command parameters if needed
- Update help text
- Ensure error handling is appropriate

**For Removed Endpoints**:

- Mark command as deprecated in help text
- Add warning when command is used
- Suggest alternative command

### 7. Update Output Formatters

If response schemas changed significantly:

1. Review `adsblol/cli_formatters.py`
2. Update table formatters to handle new/changed fields
3. Ensure JSON formatters work with new models
4. Maintain consistent styling with existing formatters
5. Handle new edge cases (missing fields, new field types)

### 8. Update Tests

Update tests to reflect specification changes:

**Test Fixtures**:

- Fetch new sample responses from updated API endpoints
- Update fixtures in `tests/fixtures/openapi_responses/`
- Ensure fixtures match new schemas

**Model Tests**:

- Update `tests/models/test_openapi_v2.py` and `tests/models/test_openapi_v0.py`
- Add tests for new models
- Update tests for changed models
- Remove tests for removed models

**Client Tests**:

- Update `tests/client/test_openapi.py`
- Add tests for new methods
- Update tests for changed methods
- Update mock responses to match new schemas
- Test new error conditions

**CLI Tests**:

- Update `tests/test_cli_openapi.py`
- Add tests for new commands
- Update tests for changed commands
- Ensure all commands produce correct output format

### 9. Update Documentation

Update documentation to reflect changes:

**API Client Documentation** (`docs/dev/openapi-client.md`):

- Document new endpoints and capabilities
- Update examples if behavior changed
- Add migration notes for breaking changes
- Update feature comparison with re-api

**Main README** (`README.md`):

- Update examples if needed
- Add new features to feature list
- Update quick start if appropriate

**Architecture Documentation** (`docs/dev/architecture.md`):

- Update if architectural patterns changed
- Document new components

**Project Context** (`openspec/project.md`):

- Update OpenAPI version number
- Document significant capability changes

### 10. Run Quality Checks

Before submitting, run all quality checks:

```bash
# Type checking
mypy adsblol

# Linting
ruff check adsblol

# Formatting
ruff format adsblol

# Run tests
pytest

# Check coverage
pytest --cov=adsblol --cov-report=term
```

Ensure:

- No mypy errors
- No linting errors
- Code is properly formatted
- All tests pass
- Coverage remains >90%

### 11. Manual Testing

Test the updated client manually:

```bash
# Test a few key v2 endpoints
adsblol openapi v2 hex 4CA87C
adsblol openapi v2 point 37.7749 -122.4194 50

# Test v0 endpoints
adsblol openapi v0 me

# Test with JSON output
adsblol openapi v2 mil --json
```

Verify:

- Commands execute without errors
- Output formatting is correct
- Data appears valid and complete

### 12. Create Pull Request

Create a pull request with:

**Title**: `Update OpenAPI client to spec version X.Y.Z`

**Description**:

- List specification changes (link to spec diff)
- Document breaking changes (if any)
- List new endpoints/features
- List deprecated/removed endpoints (if any)
- Include migration guidance for users
- Link to related GitHub issue from monitoring workflow

**Checklist**:

- [ ] Models regenerated
- [ ] Version tracking updated
- [ ] Client methods updated
- [ ] CLI commands updated
- [ ] Tests updated and passing
- [ ] Documentation updated
- [ ] Quality checks passing
- [ ] Manual testing completed

## Breaking Change Handling

If breaking changes exist:

1. **Major Version Bump**: If package uses semantic versioning, this requires a major version bump
2. **Deprecation Period**: Consider adding deprecation warnings before removing features
3. **Migration Guide**: Provide clear migration guide in CHANGELOG and docs
4. **User Communication**: Announce breaking changes prominently in release notes

## Common Issues

### Generated Models Don't Match API

- Check datamodel-code-generator version
- Verify generation command parameters
- Check for manual edits that were overwritten
- Ensure spec is valid OpenAPI 3.x format

### Tests Failing After Update

- Update test fixtures with actual API responses
- Check mock response formats match new schemas
- Update assertions for changed field names/types
- Verify test data is valid against new schemas

### Type Errors After Regeneration

- Check for circular imports in models
- Verify Pydantic v2 compatibility
- Check for missing or incorrect type hints
- Run mypy with verbose output to debug

### CLI Output Broken

- Verify formatter can handle new model structure
- Check for missing fields that table depends on
- Update column definitions if fields renamed
- Test with various response types (empty, single, multiple)

## Success Criteria

Before marking the update complete, ensure:

- [ ] All specification changes incorporated
- [ ] No breaking changes without deprecation warnings
- [ ] All tests passing with >90% coverage
- [ ] Documentation updated and accurate
- [ ] No mypy or linting errors
- [ ] Manual testing completed successfully
- [ ] PR ready for review with comprehensive description
- [ ] GitHub issue from monitoring workflow can be closed

## Notes

- This prompt should be used whenever the OpenAPI spec changes
- Keep this prompt updated as the update process evolves
- Document any new patterns or challenges encountered
- Consider automating more of this process over time
