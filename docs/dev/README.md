# Developer Documentation

**For Contributors and Library Developers**

This documentation is for developers who want to contribute to SkySnoop, extend its functionality, or understand its internal architecture. If you're looking to **use** SkySnoop in your application, see the [User Documentation](../README.md) instead.

## Who This Is For

- **Contributors**: Adding features, fixing bugs, or improving the library
- **Maintainers**: Understanding the codebase architecture and design decisions
- **Extension Developers**: Adding new backends, adapters, or integrations
- **Advanced Users**: Needing to understand internal APIs or debug issues

## For Users

If you just want to use SkySnoop to query aircraft data:

- **Start here**: [User Documentation](../README.md)
- **Getting started**: [Getting Started Guide](../getting-started.md)
- **Quick reference**: [SkySnoop Client Guide](../skysnoop-client.md)

## Architecture Overview

The skysnoop SDK provides a **three-layer architecture**:

1. **High-Level Unified Client** (`SkySnoop`): Recommended user interface with automatic backend selection and normalized `SkyData` responses
2. **Backend Adapters**: Implement `BackendProtocol` to normalize different API backends
3. **Low-Level Clients** (`OpenAPIClient`, `ReAPIClient`): Direct backend HTTP communication
4. **Shared Infrastructure**: HTTP client, query builder, models, and testing framework

This separation allows users to work with a simple, unified interface while maintainers can add new backends without changing the public API.

## Table of Contents

### Core Documentation

1. [Architecture](./architecture.md) - Three-layer architecture, SkySnoop adapter pattern, and component structure
1. [Backend Protocol](./backend-protocol.md) - Backend adapter protocol and guide for adding new API backends
1. [Testing](./testing.md) - Testing strategy and best practices with SkySnoop
1. [CLI](./cli.md) - Command-line interface development
1. [Settings](./settings.md) - Configuration and settings management

### Client Documentation

1. [SkySnoop Client](./skysnoop-client.md) - **Recommended** high-level unified client
1. [RE-API Client](./reapi-client.md) - Low-level RE-API client (advanced use cases)
1. [OpenAPI Client](./openapi-client.md) - Low-level OpenAPI client (advanced use cases)

## Deployment & Distribution

1. [Dependencies](./dependencies.md) - Dependency management
1. [Github Actions](./github.md) - CI/CD pipeline
