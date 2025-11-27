# Change: Add OpenAPI Client Support for adsb.lol API

## Why

The adsb.lol service has introduced a new OpenAPI-based REST API at `https://api.adsb.lol/` (v0 and v2) that differs from the existing readsb re-api. The new API:

- Works globally without feeder IP restrictions (unlike re-api which is feeder-only)
- Follows OpenAPI 3.1.0 standard with formal schema definitions
- Provides different endpoints and response formats than re-api
- Will require API keys in the future (feeders get keys)
- Is actively evolving (currently v0.0.2)

Currently, this library only supports the re-api at `https://re-api.adsb.lol/`. Users need access to the new OpenAPI endpoints for broader usage, and the library needs a maintenance strategy to stay synchronized with API changes.

## What Changes

- Add new OpenAPI client implementation alongside existing re-api client
- Generate Python client code from OpenAPI specification using `openapi-python-client` or similar tooling
- Create models for v2 and v0 API endpoints based on OpenAPI schemas
- Implement automated spec synchronization and client regeneration workflow
- Add CLI commands for OpenAPI endpoints
- Document differences between re-api and OpenAPI clients
- Create GitHub Copilot prompt for updating OpenAPI client when specs change
- Update project documentation to explain when to use each API

**Breaking Changes**: None - this is additive functionality. Existing re-api client remains unchanged.

## Impact

### Affected Specs

- `api-client` - Add new OpenAPI client alongside existing re-api client
- `aircraft-data-models` - Add models for OpenAPI v2 response schemas
- `cli-commands` - Add CLI commands for OpenAPI endpoints

### Affected Code

- `adsblol/client/` - New openapi client module
- `adsblol/models/` - New OpenAPI response models
- `adsblol/cli.py` - New CLI commands for OpenAPI endpoints
- `pyproject.toml` - Add openapi-python-client or datamodel-code-generator dependency
- `docs/` - New documentation for OpenAPI client usage and maintenance
- `.github/prompts/` - New prompt for OpenAPI client updates

### User Benefits

- Access adsb.lol API without feeder IP restrictions
- Future-proof implementation that stays synchronized with API changes
- Clear documentation on when to use re-api vs OpenAPI
- Standardized OpenAPI-based integration

### Maintenance Strategy

- OpenAPI spec automatically fetched from `https://api.adsb.lol/api/openapi.json`
- Client code regenerated when spec changes
- GitHub Actions workflow to check for spec updates
- Copilot prompt template for assisted manual updates when needed
