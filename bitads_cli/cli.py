#!/usr/bin/env python3

import argparse
import asyncio
from collections import defaultdict

import rich
from rich.table import Table
from rich.text import Text

from common import dependencies
from common.environ import Environ

database_manager = dependencies.get_database_manager(
    subtensor_network=Environ.SUBTENSOR_NETWORK
)
two_factor_service = dependencies.get_two_factor_service(database_manager)
unique_link_service = dependencies.get_miner_unique_link_service(database_manager)
campaign_service = dependencies.get_campaign_service(database_manager)

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
            end_section=True,
        )
    # Print the table
    console.print(table)


# New function to list active campaigns and unique links
async def async_list_unique_links():
    campaigns = await campaign_service.get_active_campaigns()

    # Print the note about full campaign info
    console.print("[bold yellow]For detailed information about all active campaigns, please visit: [link=https://bitads.ai/activeCampaigns]https://bitads.ai/activeCampaigns[/link][/bold yellow]\n")

    # Create a dictionary to group campaigns by hotkey
    hotkey_groups = defaultdict(list)

    for campaign in campaigns:
        links = await unique_link_service.get_unique_links_for_campaign(
            campaign.product_unique_id
        )

        # Group links by hotkey
        for link in links:
            hotkey_groups[link.hotkey].append({
                'campaign': campaign,
                'link': link
            })

    # Now, print one table per hotkey containing all related campaigns
    for hotkey, entries in hotkey_groups.items():
        # Create a new table for the hotkey
        table = Table(title="Active Campaigns", caption=f"Hotkey: {hotkey}")

        # Add columns
        table.add_column("Campaign")
        table.add_column("ID")
        table.add_column("Store")
        table.add_column("Registered", style="dim", width=10)
        table.add_column("Approved", style="dim", width=10)
        table.add_column("Started", style="dim", width=10)
        table.add_column("Unique Miner URL", width=50)

        # Add rows for all campaigns under the hotkey
        for entry in entries:
            campaign = entry['campaign']
            link = entry['link']
            table.add_row(
                f"[link={campaign.product_link}]{campaign.product_name}[/link]",
                campaign.product_unique_id,
                campaign.store_name,
                campaign.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                campaign.date_approved.strftime("%Y-%m-%d %H:%M:%S"),
                campaign.date_started.strftime("%Y-%m-%d %H:%M:%S"),
                f"[link={link.link}]{link.link}[/link]",
                end_section=True
            )

        # Print the table for the current hotkey
        console.print(table)


# Wrapper to run the async function in a synchronous context
def run_async_function(func):
    asyncio.run(func())


def main():
    # Set up the top-level parser
    parser = argparse.ArgumentParser(
        description="bacli: 2FA Management and Campaign CLI"
    )
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

    # 'campaigns' parent command
    parser_campaigns = subparsers.add_parser(
        "campaigns", help="Campaign related commands"
    )

    # 'active' subcommand under 'campaigns'
    parser_campaigns_active = parser_campaigns.add_subparsers(
        dest="campaigns_command", help="Campaign subcommands"
    )

    # 'active' subcommand under 'campaigns active'
    parser_active = parser_campaigns_active.add_parser(
        "active",
        help="If no unique link for a campaign is visible, please ensure that your mining script is running. "
        "The miner will receive tasks via the Ping synapse after some time. "
        "You may monitor the miner neuron’s logs for updates regarding the receipt of these links.",
    )
    parser_active.set_defaults(func=async_list_unique_links)

    # Parse arguments
    args = parser.parse_args()

    # Call the appropriate function if it exists
    if hasattr(args, "func"):
        run_async_function(args.func)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
