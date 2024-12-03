from collections import defaultdict

import rich
from rich.table import Table

console = rich.get_console()


async def async_miner_order_history(order_history_service):
    histories = await order_history_service.get_history()

    grouped_by_hotkey = defaultdict(list)
    for record in histories:
        grouped_by_hotkey[record.hotkey].append(record)

    for hotkey, entries in grouped_by_hotkey.items():
        # Create a new table for the hotkey
        table = Table(title="Miner Order History", caption=f"Hotkey: {hotkey}")

        # Add columns to the table
        table.add_column("ID", style="bold")
        table.add_column("Created At", style="dim", width=13)
        table.add_column("Updated At", style="dim", width=13)
        table.add_column("Status")
        table.add_column("Campaign ID")
        table.add_column("IP Address", width=15)
        table.add_column("User Agent")
        table.add_column("Order")

        # Add rows to the table
        for history in entries:
            table.add_row(
                history.id,
                history.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                history.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                history.status.name,  # Use the enum's value
                history.data.campaign_id or "N/A",
                history.data.ip_address or "N/A",
                history.data.user_agent or "N/A",
                "\n".join(f"{i.name} x{i.quantity}" for i in history.data.order_info.items)
            )

        # Print the table to the console
        console.print(table)
