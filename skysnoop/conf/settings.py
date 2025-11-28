from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "skysnoop"
    debug: bool = False

    # API settings
    adsb_api_base_url: str = Field(
        default="https://re-api.adsb.lol/",
        description="Base URL for the adsb.lol re-api service",
    )
    adsb_api_timeout: float = Field(
        default=30.0,
        description="HTTP timeout in seconds for API requests",
    )

    # CLI settings
    cli_output_format: Literal["table", "json"] = Field(
        default="table",
        description="Default output format for CLI commands",
    )
