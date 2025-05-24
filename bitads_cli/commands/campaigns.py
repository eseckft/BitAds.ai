import json
import operator

import pycountry
import rich
from rich.table import Table
from collections import defaultdict

console = rich.get_console()


# New function to list all campaigns (implementation to be added)
async def async_list_campaigns(campaign_service):
    campaigns = await campaign_service.get_active_campaigns()

    # Print the note about full campaign info
    console.print(
        "[bold yellow]For detailed information about all active campaigns, please visit: "
        "[link=https://bitads.ai/campaigns]https://bitads.ai/campaigns[/link]\n"
        "Or run the command[/bold yellow] [bold]bacli campaigns info {campaign_id}[/bold]"
    )

    table = Table(title="Active Campaigns")

    # Add columns
    table.add_column("Campaign")
    table.add_column("ID")
    table.add_column("Store")
    table.add_column("Registered", style="dim", width=10)
    table.add_column("Approved", style="dim", width=10)
    table.add_column("Started", style="dim", width=10)
    table.add_column("Product Link", no_wrap=True)

    for campaign in campaigns:
        table.add_row(
            f"[link={campaign.product_link}]{campaign.product_name}[/link]",
            campaign.product_unique_id,
            campaign.store_name,
            (
                campaign.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if campaign.created_at
                else "N/A"
            ),
            (
                campaign.date_approved.strftime("%Y-%m-%d %H:%M:%S")
                if campaign.date_approved
                else "N/A"
            ),
            (
                campaign.date_started.strftime("%Y-%m-%d %H:%M:%S")
                if campaign.date_started
                else "N/A"
            ),
            f"[link={campaign.product_link}]{campaign.product_link}[/link]",
            end_section=True,
        )

    console.print(table)


async def async_campaign_info(campaign_service, campaign_id: str):
    # Fetch the campaign by ID using the service
    campaign = await campaign_service.get_campaign_by_id(campaign_id)

    if not campaign:
        console.print(f"[bold red]Campaign with ID {campaign_id} not found.[/bold red]")
        return

    # Create a rich table to display the campaign details
    table = Table(title=f"Campaign Info for ID: {campaign_id}")

    # Add columns to the table
    table.add_column("Field", style="bold magenta")
    table.add_column("Value", style="bold cyan")

    # Add rows with campaign details
    table.add_row("Product Name", campaign.product_name or "N/A")
    table.add_row("Product Unique ID", campaign.product_unique_id or "N/A")
    table.add_row("Store Name", campaign.store_name or "N/A")
    table.add_row("Product Link", campaign.product_link or "N/A")
    table.add_row(
        "Created At",
        (
            campaign.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if campaign.created_at
            else "N/A"
        ),
    )
    table.add_row(
        "Date Started",
        (
            campaign.date_started.strftime("%Y-%m-%d %H:%M:%S")
            if campaign.date_started
            else "N/A"
        ),
    )
    table.add_row(
        "Date Approved",
        (
            campaign.date_approved.strftime("%Y-%m-%d %H:%M:%S")
            if campaign.date_approved
            else "N/A"
        ),
    )
    table.add_row(
        "Updated At",
        (
            campaign.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if campaign.updated_at
            else "N/A"
        ),
    )
    countries = map(
        operator.attrgetter("name"),
        filter(
            bool,
            [
                pycountry.countries.get(alpha_2=c)
                for c in json.loads(campaign.countries_approved_for_product_sales)
            ],
        ),
    )
    table.add_row("Countries Approved for Sales", ", ".join(countries))

    # Print the table using rich
    console.print(table)


async def async_list_unique_links(unique_link_service, campaign_service):
    campaigns = await campaign_service.get_active_campaigns()
    console.print(
        "[bold yellow]For detailed campaign info, visit: [link=https://bitads.ai/campaigns]"
        "https://bitads.ai/campaigns[/link][/bold yellow]"
    )

    hotkey_groups = defaultdict(list)
    for campaign in campaigns:
        links = await unique_link_service.get_unique_links_for_campaign(
            campaign.product_unique_id
        )
        for link in links:
            hotkey_groups[link.hotkey].append({"campaign": campaign, "link": link})
    # Now, print one table per hotkey containing all related campaigns
    for hotkey, entries in hotkey_groups.items():
        # Create a new table for the hotkey
        table = Table(
            title="Miner Unique Links by campaigns", caption=f"Hotkey: {hotkey}"
        )
        # Add columns
        table.add_column("Campaign")
        table.add_column("ID")
        table.add_column("Store")
        table.add_column("Registered", style="dim", width=10)
        table.add_column("Approved", style="dim", width=10)
        table.add_column("Started", style="dim", width=10)
        table.add_column("Unique Miner URL", width=50, no_wrap=True)

        # Add rows for all campaigns under the hotkey
        for entry in entries:
            campaign = entry["campaign"]
            link = entry["link"]
            table.add_row(
                f"[link={campaign.product_link}]{campaign.product_name}[/link]",
                campaign.product_unique_id,
                campaign.store_name,
                campaign.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                campaign.date_approved.strftime("%Y-%m-%d %H:%M:%S") if campaign.date_approved else 'N/A',
                campaign.date_started.strftime("%Y-%m-%d %H:%M:%S"),
                f"[link={link.link}]{link.link}[/link]",
                end_section=True,
            )

        # Print the table for the current hotkey
        console.print(table)
