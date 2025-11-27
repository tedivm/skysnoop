"""Output formatting utilities for CLI commands."""

import json
from typing import Any, Literal

from rich.console import Console
from rich.table import Table

from adsblol.models.openapi import V2ResponseModel
from adsblol.models.response import APIResponse

console = Console()


def format_output(
    response: APIResponse,
    format_type: Literal["table", "json"] = "table",
) -> None:
    """Format and display API response in the specified format.

    Args:
        response: The API response to format
        format_type: Output format - "table" for human-readable or "json" for machine-readable
    """
    if format_type == "json":
        format_json(response)
    else:
        format_table(response)


def format_json(response: APIResponse) -> None:
    """Format response as JSON and print to stdout.

    Args:
        response: The API response to format
    """
    output = response.model_dump(mode="json", exclude_none=True)
    print(json.dumps(output, indent=2))


def format_table(response: APIResponse) -> None:
    """Format response as a human-readable table.

    Args:
        response: The API response to format
    """
    if response.resultCount == 0:
        console.print("[yellow]No aircraft found matching the query.[/yellow]")
        return

    console.print(f"[bold green]Found {response.resultCount} aircraft[/bold green]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Hex", style="dim")
    table.add_column("Callsign")
    table.add_column("Registration")
    table.add_column("Type")
    table.add_column("Alt (ft)")
    table.add_column("Speed (kts)")
    table.add_column("Position")
    table.add_column("Squawk")

    for aircraft in response.aircraft:
        # Format altitude
        if aircraft.alt_baro == "ground":
            altitude = "GROUND"
        elif aircraft.alt_baro is not None:
            altitude = str(aircraft.alt_baro)
        elif aircraft.alt_geom == "ground":
            altitude = "GROUND"
        elif aircraft.alt_geom is not None:
            altitude = str(aircraft.alt_geom)
        else:
            altitude = "-"

        # Format speed
        speed = str(aircraft.gs) if aircraft.gs is not None else "-"

        # Format position
        if aircraft.lat is not None and aircraft.lon is not None:
            position = f"{aircraft.lat:.4f},{aircraft.lon:.4f}"
        else:
            position = "-"

        # Format callsign
        callsign = aircraft.flight.strip() if aircraft.flight else "-"

        # Format registration
        registration = aircraft.registration if aircraft.registration else "-"

        # Format type
        type_code = aircraft.type if aircraft.type else "-"

        # Format squawk
        squawk = aircraft.squawk if aircraft.squawk else "-"

        table.add_row(
            aircraft.hex,
            callsign,
            registration,
            type_code,
            altitude,
            speed,
            position,
            squawk,
        )

    console.print(table)


def format_compact(response: APIResponse) -> None:
    """Format response as compact output (one line per aircraft).

    Args:
        response: The API response to format
    """
    if response.resultCount == 0:
        console.print("[yellow]No aircraft found.[/yellow]")
        return

    console.print(f"[bold]Found {response.resultCount} aircraft:[/bold]\n")

    for aircraft in response.aircraft:
        parts = [aircraft.hex]

        if aircraft.flight:
            parts.append(f"CS:{aircraft.flight.strip()}")

        if aircraft.registration:
            parts.append(f"REG:{aircraft.registration}")

        if aircraft.type:
            parts.append(f"TYPE:{aircraft.type}")

        if aircraft.alt_baro == "ground":
            parts.append("ALT:GROUND")
        elif aircraft.alt_baro is not None:
            parts.append(f"ALT:{aircraft.alt_baro}ft")

        if aircraft.lat is not None and aircraft.lon is not None:
            parts.append(f"POS:{aircraft.lat:.4f},{aircraft.lon:.4f}")

        console.print(" | ".join(parts))


def format_openapi_output(
    response: V2ResponseModel | dict[str, Any],
    format_type: Literal["table", "json"] = "table",
) -> None:
    """Format and display OpenAPI response.

    Args:
        response: The OpenAPI response to format (V2ResponseModel or dict)
        format_type: Output format - "table" for human-readable or "json" for machine-readable
    """
    if format_type == "json":
        format_openapi_json(response)
    else:
        format_openapi_table(response)


def format_openapi_json(response: V2ResponseModel | dict[str, Any]) -> None:
    """Format OpenAPI response as JSON.

    Args:
        response: The OpenAPI response to format
    """
    if isinstance(response, V2ResponseModel):
        output = response.model_dump(mode="json", exclude_none=True)
    else:
        output = response
    print(json.dumps(output, indent=2))


def format_openapi_table(response: V2ResponseModel | dict[str, Any]) -> None:
    """Format OpenAPI response as a human-readable table.

    Args:
        response: The OpenAPI response to format
    """
    # Handle dict responses (v0 endpoints)
    if isinstance(response, dict):
        console.print("[bold]Response:[/bold]")
        console.print_json(data=response)
        return

    # Handle V2ResponseModel
    if response.total == 0:
        console.print("[yellow]No aircraft found matching the query.[/yellow]")
        return

    console.print(f"[bold green]Found {response.total} aircraft[/bold green]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Hex", style="dim")
    table.add_column("Callsign")
    table.add_column("Registration")
    table.add_column("Type")
    table.add_column("Alt (ft)")
    table.add_column("Speed (kts)")
    table.add_column("Position")
    table.add_column("Squawk")

    for aircraft in response.ac:
        # Format altitude
        if aircraft.alt_baro == "ground":
            altitude = "GROUND"
        elif aircraft.alt_baro is not None:
            altitude = str(aircraft.alt_baro)
        elif aircraft.alt_geom is not None:
            altitude = str(aircraft.alt_geom)
        else:
            altitude = "-"

        # Format speed
        speed = str(aircraft.gs) if aircraft.gs is not None else "-"

        # Format position
        if aircraft.lat is not None and aircraft.lon is not None:
            position = f"{aircraft.lat:.4f},{aircraft.lon:.4f}"
        else:
            position = "-"

        # Format callsign
        callsign = aircraft.flight.strip() if aircraft.flight else "-"

        # Format registration
        registration = aircraft.r if aircraft.r else "-"

        # Format type
        type_code = aircraft.t if aircraft.t else "-"

        # Format squawk
        squawk = aircraft.squawk if aircraft.squawk else "-"

        table.add_row(
            aircraft.hex,
            callsign,
            registration,
            type_code,
            altitude,
            speed,
            position,
            squawk,
        )

    console.print(table)
