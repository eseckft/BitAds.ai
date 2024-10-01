#!/usr/bin/env python3

import argparse
import asyncio

import rich
from rich.table import Table
from rich.text import Text

from common import dependencies
from common.environ import Environ

database_manager = dependencies.get_database_manager(
    subtensor_network=Environ.SUBTENSOR_NETWORK
)
two_factor_service = dependencies.get_two_factor_service(database_manager)

console = rich.get_console()

# Define asynchronous tasks (e.g., list 2FA codes)
async def async_list_2fa_codes():
    codes = await two_factor_service.get_last_codes()

    # Create a rich table
    table = Table(title="Two Factor Authentication Data")

    # Add columns
    table.add_column("Created At", style="dim", width=13)
    table.add_column("IP Address", width=15)
    table.add_column("User Agent")
    table.add_column("Hotkey")
    table.add_column("2FA Code", width=10)

    # Add rows from data
    for item in codes:
        # Truncate the hotkey to first and last N characters
        hotkey_display = item.hotkey

        # Apply color to the code field
        code_display = Text(item.code, style="bold green")

        # Add the data row
        table.add_row(
            item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "N/A",
            item.ip_address,
            item.user_agent or "N/A",
            hotkey_display,
            code_display,  # Display the colored code
            end_section=True
        )
    # Print the table
    console.print(table)

# Wrapper to run the async function in a synchronous context
def run_async_function(func):
    asyncio.run(func())

def main():
    # Set up the top-level parser
    parser = argparse.ArgumentParser(description="bacli: 2FA Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Main subcommands")

    # '2fa' parent command
    parser_2fa = subparsers.add_parser("2fa", help="2FA related commands")

    # Subparsers for '2fa' commands
    subparsers_2fa = parser_2fa.add_subparsers(
        dest="2fa_command", help="2FA subcommands"
    )

    # 'list' subcommand under '2fa'
    parser_list = subparsers_2fa.add_parser("list", help="List all 2FA codes")
    parser_list.set_defaults(func=async_list_2fa_codes)

    # Parse arguments
    args = parser.parse_args()

    # Call the appropriate function if it exists
    if hasattr(args, "func"):
        run_async_function(args.func)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()