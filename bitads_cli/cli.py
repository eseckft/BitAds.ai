#!/usr/bin/env python3

import argparse
import asyncio

from bitads_cli.commands.campaigns import (
    async_list_unique_links,
    async_list_campaigns,
    async_campaign_info,
)
from bitads_cli.commands.orders import async_miner_order_history
from bitads_cli.commands.two_fa import async_list_2fa_codes
from common import dependencies
from common.environ import Environ


def get_services():
    database_manager = dependencies.get_database_manager(
        subtensor_network=Environ.SUBTENSOR_NETWORK
    )
    return {
        "two_factor_service": dependencies.get_two_factor_service(database_manager),
        "unique_link_service": dependencies.get_miner_unique_link_service(
            database_manager
        ),
        "campaign_service": dependencies.get_campaign_service(database_manager),
        "order_history_service": dependencies.get_order_history_service(
            database_manager
        ),
    }


def run_async_function(func, *args):
    asyncio.run(func(*args))


def main():
    services = get_services()
    parser = argparse.ArgumentParser(description="bacli CLI")
    subparsers = parser.add_subparsers(dest="command", help="Main subcommands")

    parser_2fa = subparsers.add_parser("2fa", help="2FA commands")
    parser_2fa.set_defaults(
        func=lambda args: run_async_function(
            async_list_2fa_codes, services["two_factor_service"]
        )
    )

    # 'campaigns' parent command
    parser_campaigns = subparsers.add_parser(
        "campaigns", help="Campaign related commands"
    )

    # 'active' subcommand under 'campaigns'
    subparser_campaigns = parser_campaigns.add_subparsers(
        dest="campaigns_command", help="Campaign subcommands"
    )

    # 'links' subcommand under 'campaigns'
    subparser_campaigns.add_parser(
        "links",
        help="If no unique link for a campaign is visible, please ensure that your mining script is running. "
        "The miner will receive tasks via the Ping synapse after some time. "
        "You may monitor the miner neuron’s logs for updates regarding the receipt of these links.",
    ).set_defaults(
        func=lambda args: run_async_function(
            async_list_unique_links,  # This function handles the history command
            services["unique_link_service"],  # Pass the required service
            services["campaign_service"],  # Pass the required service
        )
    )

    # 'list' subcommand under 'campaigns'
    subparser_campaigns.add_parser("list", help="List all campaigns").set_defaults(
        func=lambda args: run_async_function(
            async_list_campaigns,  # This function handles the history command
            services["campaign_service"],  # Pass the required service
        )
    )

    # 'info' subcommand under 'campaigns'
    parser_info = subparser_campaigns.add_parser(
        "info", help="Display information for a specific campaign by ID"
    )
    parser_info.add_argument(
        "campaign_id", type=str, help="The ID of the campaign to retrieve info for"
    )
    parser_info.set_defaults(
        func=lambda args: run_async_function(
            async_campaign_info,  # This function handles the history command
            services["campaign_service"],  # Pass the required service
            args.campaign_id,
        )
    )

    # Orders Commands
    parser_orders = subparsers.add_parser("orders", help="Orders-related commands")
    orders_subparsers = parser_orders.add_subparsers(
        dest="orders_command", help="Orders subcommands"
    )

    # Orders -> History Command
    parser_orders_history = orders_subparsers.add_parser(
        "history", help="Show order history"
    )
    parser_orders_history.set_defaults(
        func=lambda args: run_async_function(
            async_miner_order_history,  # This function handles the history command
            services["order_history_service"],  # Pass the required service
        )
    )

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
