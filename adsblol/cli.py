import asyncio
from functools import wraps
from typing import Optional

import typer

from .cli_formatters import format_output
from .client.api import ADSBLolClient
from .exceptions import ADSBLolError, APIError, TimeoutError, ValidationError
from .query.filters import QueryFilters
from .settings import settings

app = typer.Typer()


def syncify(f):
    """This simple decorator converts an async function into a sync function,
    allowing it to work with Typer.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def handle_errors(f):
    """Decorator to handle common errors in CLI commands."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TimeoutError as e:
            typer.echo(f"Error: Request timed out - {e}", err=True)
            typer.echo("The API took too long to respond. Please try again.", err=True)
            raise typer.Exit(code=1)
        except APIError as e:
            typer.echo(f"Error: API request failed - {e}", err=True)
            typer.echo("Please check your parameters and try again.", err=True)
            raise typer.Exit(code=1)
        except ValidationError as e:
            typer.echo(f"Error: Invalid parameters - {e}", err=True)
            raise typer.Exit(code=1)
        except ADSBLolError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"Unexpected error: {e}", err=True)
            raise typer.Exit(code=1)

    return wrapper


@app.command(help=f"Display the current installed version of {settings.project_name}.")
def version():
    from . import __version__

    typer.echo(f"{settings.project_name} - {__version__}")


@app.command(help="Query aircraft within a radius of a point (lat, lon).")
@handle_errors
@syncify
async def circle(
    lat: float = typer.Argument(..., help="Latitude of center point"),
    lon: float = typer.Argument(..., help="Longitude of center point"),
    radius: float = typer.Argument(..., help="Radius in nautical miles"),
    callsign_exact: Optional[str] = typer.Option(None, "--callsign", help="Filter by exact callsign"),
    callsign_prefix: Optional[str] = typer.Option(None, "--callsign-prefix", help="Filter by callsign prefix"),
    type_code: Optional[str] = typer.Option(None, "--type", help="Filter by aircraft type code"),
    squawk: Optional[str] = typer.Option(None, "--squawk", help="Filter by squawk code"),
    above_alt_baro: Optional[int] = typer.Option(None, "--above-alt", help="Filter above altitude (feet)"),
    below_alt_baro: Optional[int] = typer.Option(None, "--below-alt", help="Filter below altitude (feet)"),
    military: Optional[bool] = typer.Option(None, "--military", help="Filter for military aircraft"),
    interesting: Optional[bool] = typer.Option(None, "--interesting", help="Filter for interesting aircraft"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Query aircraft within a circular area."""
    filters = _build_filters(
        callsign_exact=callsign_exact,
        callsign_prefix=callsign_prefix,
        type_code=type_code,
        squawk=squawk,
        above_alt_baro=above_alt_baro,
        below_alt_baro=below_alt_baro,
        military=military,
        interesting=interesting,
    )

    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.circle(lat=lat, lon=lon, radius=radius, filters=filters)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Query the closest aircraft to a point.")
@handle_errors
@syncify
async def closest(
    lat: float = typer.Argument(..., help="Latitude of center point"),
    lon: float = typer.Argument(..., help="Longitude of center point"),
    radius: float = typer.Argument(..., help="Maximum search radius in nautical miles"),
    callsign_exact: Optional[str] = typer.Option(None, "--callsign", help="Filter by exact callsign"),
    callsign_prefix: Optional[str] = typer.Option(None, "--callsign-prefix", help="Filter by callsign prefix"),
    type_code: Optional[str] = typer.Option(None, "--type", help="Filter by aircraft type code"),
    squawk: Optional[str] = typer.Option(None, "--squawk", help="Filter by squawk code"),
    above_alt_baro: Optional[int] = typer.Option(None, "--above-alt", help="Filter above altitude (feet)"),
    below_alt_baro: Optional[int] = typer.Option(None, "--below-alt", help="Filter below altitude (feet)"),
    military: Optional[bool] = typer.Option(None, "--military", help="Filter for military aircraft"),
    interesting: Optional[bool] = typer.Option(None, "--interesting", help="Filter for interesting aircraft"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Query the closest aircraft to a point within a maximum radius."""
    filters = _build_filters(
        callsign_exact=callsign_exact,
        callsign_prefix=callsign_prefix,
        type_code=type_code,
        squawk=squawk,
        above_alt_baro=above_alt_baro,
        below_alt_baro=below_alt_baro,
        military=military,
        interesting=interesting,
    )

    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.closest(lat=lat, lon=lon, radius=radius, filters=filters)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Query aircraft within a bounding box.")
@handle_errors
@syncify
async def box(
    lat_south: float = typer.Argument(..., help="Southern latitude boundary"),
    lat_north: float = typer.Argument(..., help="Northern latitude boundary"),
    lon_west: float = typer.Argument(..., help="Western longitude boundary"),
    lon_east: float = typer.Argument(..., help="Eastern longitude boundary"),
    callsign_exact: Optional[str] = typer.Option(None, "--callsign", help="Filter by exact callsign"),
    callsign_prefix: Optional[str] = typer.Option(None, "--callsign-prefix", help="Filter by callsign prefix"),
    type_code: Optional[str] = typer.Option(None, "--type", help="Filter by aircraft type code"),
    squawk: Optional[str] = typer.Option(None, "--squawk", help="Filter by squawk code"),
    above_alt_baro: Optional[int] = typer.Option(None, "--above-alt", help="Filter above altitude (feet)"),
    below_alt_baro: Optional[int] = typer.Option(None, "--below-alt", help="Filter below altitude (feet)"),
    military: Optional[bool] = typer.Option(None, "--military", help="Filter for military aircraft"),
    interesting: Optional[bool] = typer.Option(None, "--interesting", help="Filter for interesting aircraft"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Query aircraft within a rectangular bounding box."""
    filters = _build_filters(
        callsign_exact=callsign_exact,
        callsign_prefix=callsign_prefix,
        type_code=type_code,
        squawk=squawk,
        above_alt_baro=above_alt_baro,
        below_alt_baro=below_alt_baro,
        military=military,
        interesting=interesting,
    )

    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.box(
            lat_south=lat_south,
            lat_north=lat_north,
            lon_west=lon_west,
            lon_east=lon_east,
            filters=filters,
        )

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Find aircraft by ICAO hex code.")
@handle_errors
@syncify
async def find_hex(
    hex_code: str = typer.Argument(..., help="ICAO 24-bit hex code (e.g., a12345)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Find a specific aircraft by its ICAO hex code."""
    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.find_hex(hex_code)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Find aircraft by callsign.")
@handle_errors
@syncify
async def find_callsign(
    callsign: str = typer.Argument(..., help="Aircraft callsign (e.g., UAL123)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Find aircraft by their callsign."""
    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.find_callsign(callsign)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Find aircraft by registration.")
@handle_errors
@syncify
async def find_reg(
    registration: str = typer.Argument(..., help="Aircraft registration (e.g., N12345)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Find a specific aircraft by its registration."""
    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.find_reg(registration)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Find aircraft by type code.")
@handle_errors
@syncify
async def find_type(
    type_code: str = typer.Argument(..., help="Aircraft type code (e.g., A321, B738)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Find all aircraft of a specific type."""
    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        response = await client.find_type(type_code)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


@app.command(help="Query all aircraft, optionally including those without position.")
@handle_errors
@syncify
async def all_aircraft(
    include_no_position: bool = typer.Option(
        False,
        "--include-no-position",
        help="Include aircraft without position data",
    ),
    callsign_exact: Optional[str] = typer.Option(None, "--callsign", help="Filter by exact callsign"),
    callsign_prefix: Optional[str] = typer.Option(None, "--callsign-prefix", help="Filter by callsign prefix"),
    type_code: Optional[str] = typer.Option(None, "--type", help="Filter by aircraft type code"),
    squawk: Optional[str] = typer.Option(None, "--squawk", help="Filter by squawk code"),
    above_alt_baro: Optional[int] = typer.Option(None, "--above-alt", help="Filter above altitude (feet)"),
    below_alt_baro: Optional[int] = typer.Option(None, "--below-alt", help="Filter below altitude (feet)"),
    military: Optional[bool] = typer.Option(None, "--military", help="Filter for military aircraft"),
    interesting: Optional[bool] = typer.Option(None, "--interesting", help="Filter for interesting aircraft"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Query all aircraft currently tracked by the API.

    By default, only aircraft with position data are returned.
    Use --include-no-position to include aircraft without position.
    """
    filters = _build_filters(
        callsign_exact=callsign_exact,
        callsign_prefix=callsign_prefix,
        type_code=type_code,
        squawk=squawk,
        above_alt_baro=above_alt_baro,
        below_alt_baro=below_alt_baro,
        military=military,
        interesting=interesting,
    )

    async with ADSBLolClient(
        base_url=settings.adsb_api_base_url,
        timeout=settings.adsb_api_timeout,
    ) as client:
        if include_no_position:
            response = await client.all(filters=filters)
        else:
            response = await client.all_with_pos(filters=filters)

    output_format = "json" if json_output else settings.cli_output_format
    format_output(response, format_type=output_format)


def _build_filters(
    callsign_exact: Optional[str] = None,
    callsign_prefix: Optional[str] = None,
    type_code: Optional[str] = None,
    squawk: Optional[str] = None,
    above_alt_baro: Optional[int] = None,
    below_alt_baro: Optional[int] = None,
    military: Optional[bool] = None,
    interesting: Optional[bool] = None,
) -> Optional[QueryFilters]:
    """Build QueryFilters from CLI options.

    Args:
        callsign_exact: Exact callsign to filter by
        callsign_prefix: Callsign prefix to filter by
        type_code: Aircraft type code to filter by
        squawk: Squawk code to filter by
        above_alt_baro: Minimum altitude in feet
        below_alt_baro: Maximum altitude in feet
        military: Filter for military aircraft
        interesting: Filter for interesting aircraft

    Returns:
        QueryFilters instance if any filters are set, None otherwise
    """
    filter_params = {
        "callsign_exact": callsign_exact,
        "callsign_prefix": callsign_prefix,
        "type_code": type_code,
        "squawk": squawk,
        "above_alt_baro": above_alt_baro,
        "below_alt_baro": below_alt_baro,
        "mil": military,
        "pia": interesting,
    }

    # Remove None values
    filter_params = {k: v for k, v in filter_params.items() if v is not None}

    if not filter_params:
        return None

    return QueryFilters(**filter_params)


if __name__ == "__main__":
    app()
