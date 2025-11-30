"""Backend selection logic for SkySnoop client.

This module provides the logic for automatically selecting the most appropriate
backend (OpenAPI or RE-API) based on available configuration and API accessibility.

Selection Strategy:
    The automatic backend selection follows this priority:

    1. API Key Provided → OpenAPI
       - Prepares for future API key requirement
       - Ensures API key is used when available

    2. No API Key + prefer_reapi=True → RE-API (DEFAULT)
       - Preferred stable backend with full feature support
       - Native operations (no simulation)
       - Full QueryFilters support
       - Requires feeder access

    3. No API Key + prefer_reapi=False → OpenAPI
       - Public access fallback
       - Simulated geographic operations
       - Limited filter support

Design Rationale:
    RE-API is preferred by default because:
    - Native support for all operations (no simulation overhead)
    - Full QueryFilters support
    - More efficient (no need to fetch all aircraft for geographic queries)
    - Proven stable backend

    OpenAPI is used when:
    - API key is provided (future-proofing)
    - Public access is needed (no feeder)
    - Explicitly requested
"""

import logging
from typing import Literal

logger = logging.getLogger(__name__)

BackendType = Literal["openapi", "reapi"]


async def select_backend(
    api_key: str | None = None,
    prefer_reapi: bool = True,
) -> BackendType:
    """Automatically select the most appropriate backend.

    Selection logic:
    1. If API key provided → OpenAPI (for future API key requirement)
    2. If no API key and prefer_reapi → RE-API (stable, preferred backend)
    3. Otherwise → OpenAPI (fallback)

    Currently neither backend requires an API key, but OpenAPI may in the future.
    RE-API is preferred when no API key is provided as it's the stable backend
    with full feature support (box queries, all_with_pos, no simulation needed).

    Args:
        api_key: Optional API key for OpenAPI backend
        prefer_reapi: Whether to prefer RE-API when no API key provided (default True)

    Returns:
        Selected backend type ("openapi" or "reapi")

    Examples:
        >>> # Auto-select with no API key → RE-API (preferred)
        >>> backend = await select_backend()
        >>> assert backend == "reapi"
        >>>
        >>> # API key provided → OpenAPI
        >>> backend = await select_backend(api_key="abc123")
        >>> assert backend == "openapi"
        >>>
        >>> # Disable RE-API preference → OpenAPI
        >>> backend = await select_backend(prefer_reapi=False)
        >>> assert backend == "openapi"
    """
    # API key provided → use OpenAPI (for future compatibility)
    if api_key:
        logger.info("API key provided, selecting OpenAPI backend")
        return "openapi"

    # Prefer RE-API when available (stable backend with full feature support)
    if prefer_reapi:
        logger.info("No API key, selecting RE-API backend (preferred stable backend)")
        return "reapi"

    # Fallback to OpenAPI
    logger.info("Falling back to OpenAPI backend")
    return "openapi"


def select_backend_sync(
    api_key: str | None = None,
    prefer_reapi: bool = True,
) -> BackendType:
    """Synchronous version of select_backend() for non-async contexts.

    See select_backend() for full documentation.

    Args:
        api_key: Optional API key for OpenAPI backend
        prefer_reapi: Whether to prefer RE-API when no API key provided (default True)

    Returns:
        Selected backend type ("openapi" or "reapi")
    """
    # API key provided → use OpenAPI
    if api_key:
        logger.info("API key provided, selecting OpenAPI backend")
        return "openapi"

    # Prefer RE-API when available
    if prefer_reapi:
        logger.info("No API key, selecting RE-API backend (preferred stable backend)")
        return "reapi"

    # Fallback to OpenAPI
    logger.info("Falling back to OpenAPI backend")
    return "openapi"
