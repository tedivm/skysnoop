# Design: OpenAPI Client Support

## Overview

This design introduces support for the adsb.lol OpenAPI v2 and v0 endpoints alongside the existing re-api client. The implementation prioritizes automated code generation from OpenAPI schemas to minimize manual maintenance and ensure type safety.

### System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        CLI[CLI Commands]
        UserCode[User Python Code]
    end

    subgraph "Client Layer"
        ReAPI[ADSBLolClient<br/>re-api]
        OpenAPI[OpenAPIClient<br/>OpenAPI]
        V2[V2Methods]
        V0[V0Methods]
    end

    subgraph "HTTP Layer"
        Base[BaseHTTPClient<br/>shared]
        HTTPX[httpx.AsyncClient]
    end

    subgraph "Model Layer"
        ReModels[re-api Models<br/>Aircraft, APIResponse]
        OpenModels[OpenAPI Models<br/>Generated]
        V2Models[V2Response_Model<br/>V2Response_AcItem]
        V0Models[V0 Models]
    end

    subgraph "External APIs"
        ReAPIEndpoint[https://re-api.adsb.lol<br/>Feeder-Only]
        OpenAPIEndpoint[https://api.adsb.lol<br/>Global Access]
    end

    CLI --> ReAPI
    CLI --> OpenAPI
    UserCode --> ReAPI
    UserCode --> OpenAPI

    ReAPI --> Base
    OpenAPI --> V2
    OpenAPI --> V0
    V2 --> Base
    V0 --> Base

    Base --> HTTPX

    HTTPX --> ReAPIEndpoint
    HTTPX --> OpenAPIEndpoint

    ReAPI -.uses.-> ReModels
    V2 -.uses.-> V2Models
    V0 -.uses.-> V0Models

    V2Models -.part of.-> OpenModels
    V0Models -.part of.-> OpenModels

    style ReAPI fill:#e1f5ff
    style OpenAPI fill:#ffe1e1
    style Base fill:#e1ffe1
    style OpenModels fill:#fff4e1
```

## Architecture Decisions

### Dual Client Strategy

**Decision**: Maintain separate client implementations for re-api and OpenAPI rather than creating a unified abstraction.

**Rationale**:

- Different authentication models (IP-based vs API keys)
- Different response formats and data structures
- Different use cases (re-api for feeders, OpenAPI for general use)
- Attempting to abstract would create leaky abstractions and complicate both implementations

**Implementation**:

- Keep existing `adsblol.client.api.ADSBLolClient` for re-api (unchanged)
- Add new `adsblol.client.openapi.OpenAPIClient` for OpenAPI endpoints
- Users explicitly choose which client based on their needs

### Code Generation Approach

**Decision**: Use `datamodel-code-generator` to generate Pydantic models from OpenAPI spec, with manual client methods.

**Rationale**:

- `datamodel-code-generator` generates clean Pydantic v2 models from OpenAPI schemas
- Full client generators (like `openapi-python-client`) create opinionated structure that may conflict with project conventions
- Manual client methods provide control over API design and error handling
- Generated models ensure type safety and stay synchronized with API schema

**Alternative Considered**: `openapi-python-client` - rejected due to rigid output structure and difficulty integrating with existing patterns.

### Model Organization

**Decision**: Generate OpenAPI models in `adsblol/models/openapi/` with separate modules for v0 and v2.

**Structure**:

```text
adsblol/models/
├── aircraft.py           # Existing re-api models
├── response.py           # Existing re-api models
└── openapi/
    ├── __init__.py
    ├── v2.py             # Generated v2 models
    └── v0.py             # Generated v0 models
```

```mermaid
graph LR
    subgraph "adsblol/models/"
        subgraph "Re-API Models"
            A[aircraft.py<br/>Aircraft]
            B[response.py<br/>APIResponse]
        end

        subgraph "openapi/"
            C[v2.py<br/>V2Response_Model<br/>V2Response_AcItem<br/>V2Response_LastPosition]
            D[v0.py<br/>V0 Models]
            E[__init__.py]
        end
    end

    F[ADSBLolClient] -.uses.-> A
    F -.uses.-> B
    G[OpenAPIClient.v2] -.uses.-> C
    H[OpenAPIClient.v0] -.uses.-> D

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#ffe1e1
    style D fill:#ffe1e1
```

**Rationale**:

- Isolates OpenAPI models from re-api models
- Version-specific modules support multiple API versions
- Clear namespace prevents confusion between API types

### Client Implementation Pattern

**Decision**: OpenAPI client follows same async context manager pattern as re-api client.

**Pattern**:

```python
async with OpenAPIClient(api_key=key) as client:
    response = await client.v2.get_aircraft_by_hex(hex="abc123")
```

**Rationale**:

- Consistency with existing ADSBLolClient API
- Proper resource cleanup via context managers
- Natural async/await syntax for users

### Versioned API Access

**Decision**: Organize methods by API version (v2, v0) rather than by operation type.

**Structure**:

```python
class OpenAPIClient:
    def __init__(self, base_url, api_key):
        self.v2 = V2Methods(self)
        self.v0 = V0Methods(self)
```

```mermaid
classDiagram
    class OpenAPIClient {
        +str base_url
        +str api_key
        +V2Methods v2
        +V0Methods v0
        +__aenter__()
        +__aexit__()
    }

    class V2Methods {
        -OpenAPIClient client
        +get_pia() V2Response_Model
        +get_mil() V2Response_Model
        +get_ladd() V2Response_Model
        +get_by_squawk(squawk) V2Response_Model
        +get_by_type(type) V2Response_Model
        +get_by_registration(reg) V2Response_Model
        +get_by_hex(hex) V2Response_Model
        +get_by_callsign(call) V2Response_Model
        +get_by_point(lat, lon, radius) V2Response_Model
        +get_closest(lat, lon, radius) V2Response_Model
    }

    class V0Methods {
        -OpenAPIClient client
        +get_airport(icao) dict
        +get_routes(planes) dict
        +get_me() dict
    }

    class BaseHTTPClient {
        +get(query_string) dict
        +__aenter__()
        +__aexit__()
    }

    OpenAPIClient *-- V2Methods
    OpenAPIClient *-- V0Methods
    OpenAPIClient ..> BaseHTTPClient : uses
    V2Methods ..> BaseHTTPClient : uses
    V0Methods ..> BaseHTTPClient : uses
```

**Rationale**:

- Makes API version explicit in code
- Prevents conflicts between versions with same operation names
- Allows version-specific behavior and deprecation

### Automated Update Strategy

**Decision**: Implement multi-layered update strategy combining automation and AI assistance.

**Layers**:

1. **GitHub Action for Monitoring**: Weekly check for spec changes
   - Fetches `https://api.adsb.lol/api/openapi.json`
   - Compares hash against stored version
   - Creates issue when changes detected

2. **GitHub Action for CI Testing**: Run on every PR and push to main
   - Run unit tests with mocked responses (always)
   - Run OpenAPI live tests with `pytest --run-live-openapi`
   - Uses globally accessible API (no feeder IP required)
   - Validates OpenAPI client against real API endpoints
   - Note: re-api tests remain skipped in CI (require feeder IP)

3. **Make Target for Regeneration**: `make openapi-update`
   - Downloads latest spec
   - Runs `datamodel-code-generator`
   - Updates generated models
   - Developers run tests and update manual code as needed

4. **GitHub Copilot Prompt**: `.github/prompts/update-openapi-client.prompt.md`
   - Guides agent through update process
   - Checks for breaking changes in spec
   - Updates client methods to match new endpoints
   - Updates tests for new/changed operations

**Rationale**:

- Automation catches changes quickly
- CI tests validate OpenAPI client against real API on every change
- OpenAPI's global accessibility enables CI testing (unlike feeder-only re-api)
- Live tests in CI catch breaking changes before release
- Make target simplifies regeneration
- Copilot prompt provides guided assistance for non-mechanical changes
- Combination reduces maintenance burden while maintaining quality

### API Key Management

**Decision**: Support API keys via environment variable and parameter, with graceful handling of absence.

**Implementation**:

```python
class OpenAPIClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.adsb.lol"):
        self.api_key = api_key or os.getenv("ADSBLOL_API_KEY")
        # No warning logged - API keys not required yet
```

**Rationale**:

- API keys not yet required but planned for future
- No warning to avoid annoying users until keys are actually required
- Environment variable follows 12-factor app principles
- Optional parameter supports explicit configuration
- When keys become mandatory, client will raise error on requests, not on initialization

## Data Flow

### OpenAPI Client Request Flow

```mermaid
sequenceDiagram
    participant User as User Code
    participant Client as OpenAPIClient
    participant V2 as V2Methods
    participant Base as BaseHTTPClient
    participant HTTP as httpx.AsyncClient
    participant API as adsb.lol API
    participant Model as Pydantic Models

    User->>Client: await client.v2.get_aircraft_by_hex("abc123")
    Client->>V2: get_aircraft_by_hex("abc123")
    V2->>V2: Validate parameters
    V2->>Base: get("/v2/hex/abc123")
    Base->>HTTP: GET https://api.adsb.lol/v2/hex/abc123
    HTTP->>API: HTTP GET Request
    API-->>HTTP: JSON Response
    HTTP-->>Base: Response data
    Base->>Model: Parse into V2Response_Model
    Model-->>Base: Validated model instance
    Base-->>V2: V2Response_Model
    V2-->>Client: V2Response_Model
    Client-->>User: Typed response object
```

### Update Flow

```mermaid
flowchart TD
    A[GitHub Action<br/>Weekly Schedule] --> B[Fetch openapi.json<br/>from API]
    B --> C{Hash Changed?}
    C -->|No| D[End - No Action]
    C -->|Yes| E[Create GitHub Issue<br/>with Change Details]
    E --> F[Developer Notified]
    F --> G[Developer Runs<br/>make openapi-update]
    G --> H[Download Latest Spec]
    H --> I[Run datamodel-code-generator]
    I --> J[Models Regenerated]
    J --> K[Developer Reviews Diff]
    K --> L{Breaking<br/>Changes?}
    L -->|Yes| M[Developer Invokes<br/>Copilot Prompt]
    L -->|No| N[Update Client Methods<br/>Manually]
    M --> O[Copilot Reviews Changes]
    O --> P[Copilot Updates<br/>Client Methods]
    P --> Q[Copilot Updates Tests]
    Q --> R[Developer Reviews<br/>Copilot Changes]
    N --> S[Update Tests]
    R --> T[Run Quality Checks]
    S --> T
    T --> U{Tests Pass?}
    U -->|No| V[Fix Issues]
    V --> T
    U -->|Yes| W[Create Pull Request]
    W --> X[PR Review & Merge]
```

## Error Handling

### API Errors

- 422 Validation Errors: Parse error details from response, raise `ValidationError` with field-level details
- 4xx Client Errors: Raise `APIError` with status code and message
- 5xx Server Errors: Raise `APIError` with retry guidance
- Network Errors: Raise `APIError` wrapping underlying httpx exception

```mermaid
flowchart TD
    A[API Request] --> B{Response<br/>Status?}

    B -->|200 OK| C[Parse JSON]
    C --> D{Valid<br/>Schema?}
    D -->|Yes| E[Return Typed Model]
    D -->|No| F[Raise APIError<br/>Invalid Response]

    B -->|422| G[Parse Error Details]
    G --> H[Raise ValidationError<br/>with Field Details]

    B -->|401| I[Raise AuthenticationError<br/>Invalid/Missing Key]

    B -->|429| J[Extract Retry-After]
    J --> K[Raise RateLimitError<br/>with Retry Info]

    B -->|4xx Other| L[Raise APIError<br/>Client Error]

    B -->|5xx| M[Raise APIError<br/>Server Error<br/>+ Retry Guidance]

    B -->|Network Error| N[Raise APIError<br/>Network Failure]

    style E fill:#90EE90
    style F fill:#FFB6C1
    style H fill:#FFB6C1
    style I fill:#FFB6C1
    style K fill:#FFD700
    style L fill:#FFB6C1
    style M fill:#FFB6C1
    style N fill:#FFB6C1
```

### Version Compatibility

- Store API version from spec in generated code
- Log warning if spec version changes unexpectedly
- Include version in error messages for debugging

## Testing Strategy

### Generated Model Tests

- Validate models parse successfully against fixtures from actual API responses
- Test serialization and deserialization round-trips
- Verify optional field handling

### Client Method Tests

- Use `respx` to mock HTTP responses
- Test each endpoint method with success and error cases
- Verify proper parameter validation
- Test async context manager lifecycle

### Integration Tests

- Optional tests against live OpenAPI (will require API key in future)
- Marked with pytest `live_openapi` marker (distinct from `live_api` for re-api)
- Run with `pytest --run-live-openapi` flag
- Can run in GitHub Actions (unlike re-api which requires feeder IP)
- Skipped by default when flag not provided
- Add new pytest configuration in `conftest.py`:
  - New `--run-live-openapi` command line option
  - New `live_openapi` marker registration
  - Skip logic similar to existing `live_api` marker
- Document in test docstring that API key will be required in future

## Migration Path for Users

### Documentation Structure

Create `docs/dev/openapi-client.md` covering:

1. When to use OpenAPI vs re-api
   - OpenAPI: General use, no feeder requirement, will require API key, globally accessible
   - re-api: Feeders only, more detailed data, IP-restricted (can't use from CI/GitHub Actions)

2. API key acquisition process
   - Sign up as feeder
   - Obtain key from adsb.lol dashboard
   - Set environment variable

3. Basic usage examples
4. Differences in data models
5. Migration guide from re-api to OpenAPI (when applicable)
6. Testing guidance
   - re-api tests: `pytest --run-live-api` (requires feeder IP, skipped in CI)
   - OpenAPI tests: `pytest --run-live-openapi` (can run anywhere, including CI)

### CLI Integration

Add new subcommands:

- `adsblol openapi` - Root command for OpenAPI operations
- `adsblol openapi v2 hex <hex>` - V2 hex lookup
- `adsblol openapi v2 circle <lat> <lon> <radius>` - V2 circle query
- Similar for v0 endpoints

Keep existing commands unchanged, operating on re-api.

## Security Considerations

### API Key Storage

- Never log API keys
- Use `SecretStr` type for keys in settings
- Recommend environment variables over command-line arguments
- Document secure key management practices

### Rate Limiting

- Implement client-side rate limiting to be respectful
- Log warnings when approaching limits
- Provide configuration for rate limit thresholds

## CI/CD Integration

### GitHub Actions Workflows

**Primary Test Workflow** (runs on PR and push to main):

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    steps:
      - name: Run unit tests
        run: pytest tests/ -v --cov

      - name: Run OpenAPI live tests
        run: pytest tests/integration/test_live_openapi.py -v --run-live-openapi
        # Future: add API key from secrets when required
        # env:
        #   ADSBLOL_API_KEY: ${{ secrets.ADSBLOL_API_KEY }}
```

**Spec Monitoring Workflow** (runs weekly):

```yaml
name: Check OpenAPI Spec
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
jobs:
  check-spec:
    steps:
      - name: Download latest spec
        run: curl -s https://api.adsb.lol/api/openapi.json > latest_spec.json

      - name: Compare with stored spec
        run: |
          if ! cmp -s latest_spec.json openapi_spec.json; then
            # Create GitHub issue with spec changes
          fi
```

**Key Points**:

- OpenAPI live tests run in CI (globally accessible)
- re-api tests remain skipped in CI (require feeder IP)
- Spec monitoring runs weekly to catch API changes
- CI validates client against real API on every change

## Maintenance Tooling

### Makefile Targets

```makefile
.PHONY: openapi-download
openapi-download:
    curl -s https://api.adsb.lol/api/openapi.json > openapi_spec.json

.PHONY: openapi-generate
openapi-generate: openapi-download
    datamodel-codegen --input openapi_spec.json \
        --output adsblol/models/openapi/ \
        --target-python-version 3.10 \
        --use-double-quotes \
        --output-model-type pydantic_v2.BaseModel

.PHONY: openapi-update
openapi-update: openapi-generate
    @echo "Models regenerated. Review changes and update client methods."
    @echo "Consider running: copilot @.github/prompts/update-openapi-client.prompt.md"
```

### Version Tracking

Store spec version and hash in `adsblol/client/openapi_version.py`:

```python
# Auto-generated - do not edit
OPENAPI_VERSION = "0.0.2"
SPEC_HASH = "abc123..."
SPEC_UPDATED = "2025-11-17"
```

This allows runtime version checks and debugging.

## Future Considerations

### API Key Requirement

When API keys become mandatory:

1. Update client to raise error if key not provided
2. Update documentation with key requirement
3. Consider migration guide for existing users
4. May need deprecation cycle for keyless operation

### Additional API Versions

If v3 or later versions are released:

1. Generate new `adsblol/models/openapi/v3.py`
2. Add `client.v3` methods
3. Maintain backward compatibility with older versions
4. Document version differences and migration paths

### Response Caching

Consider adding optional caching layer:

- Cache keyed by (endpoint, params)
- Configurable TTL (default 1 second, matching typical API cache)
- Useful for rapid successive queries
- Implementation deferred until user demand proven
