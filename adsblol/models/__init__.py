"""Data models for adsb.lol API responses."""

from .aircraft import Aircraft
from .response import APIResponse

# OpenAPI models available in adsblol.models.openapi submodule

__all__ = ["Aircraft", "APIResponse"]
