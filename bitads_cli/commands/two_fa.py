import rich

console = rich.get_console()

from rich.table import Table
from rich.text import Text


def format_2fa_table(codes):
    table = Table(title="Two Factor Authentication Data")
    table.add_column("Created At", style="dim", width=13)
    table.add_column("IP Address", width=15)
    table.add_column("User Agent")
    table.add_column("Hotkey")
    table.add_column("2FA Code", width=10)

    for item in codes:
        hotkey_display = item.hotkey
        code_display = Text(item.code, style="bold green")
        table.add_row(
            item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "N/A",
            item.ip_address,
            item.user_agent or "N/A",
            hotkey_display,
            code_display,
            end_section=True,
        )
    return table


async def async_list_2fa_codes(two_factor_service):
    codes = await two_factor_service.get_last_codes()
    table = format_2fa_table(codes)
    console.print(table)
