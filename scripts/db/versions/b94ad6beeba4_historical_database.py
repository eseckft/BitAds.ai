"""historical database

Revision ID: b94ad6beeba4
Revises: 72ece7221a34
Create Date: 2024-12-09 16:44:42.806814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'b94ad6beeba4'
down_revision: Union[str, None] = '72ece7221a34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def table_exists(table_name):
    """Checks if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()



def upgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_validator_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_validator_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_miner_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    if not table_exists("user_agent_activity"):
        op.create_table('user_agent_activity',
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('user_agent', 'created_at')
        )
    if not table_exists("visitor_activity"):
        op.create_table('visitor_activity',
        sa.Column('ip', sa.String(), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('ip', 'created_at')
        )
    if not table_exists("visitors"):
        op.create_table('visitors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('referer', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('country_code', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=False),
        sa.Column('campaign_item', sa.String(), nullable=False),
        sa.Column('miner_hotkey', sa.String(), nullable=False),
        sa.Column('miner_block', sa.Integer(), nullable=False),
        sa.Column('at', sa.Boolean(), nullable=False),
        sa.Column('device', sa.Enum('PC', 'MOBILE', name='device'), nullable=True),
        sa.Column('is_unique', sa.Boolean(), nullable=False),
        sa.Column('return_in_site', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Enum('new', 'synced', 'completed', name='visitstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    # ### end Alembic commands ###


def downgrade_miner_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visitors')
    op.drop_table('visitor_activity')
    op.drop_table('user_agent_activity')
    # ### end Alembic commands ###


def upgrade_validator_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    if not table_exists("bitads_data"):
        op.create_table('bitads_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('country_code', sa.String(), nullable=True),
        sa.Column('at', sa.Boolean(), nullable=False),
        sa.Column('is_unique', sa.Boolean(), nullable=False),
        sa.Column('device', sa.Enum('PC', 'MOBILE', name='device'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('sales_status', sa.Enum('NEW', 'COMPLETED', name='salesstatus'), server_default=sa.text('NEW'), nullable=False),
        sa.Column('complete_block', sa.Integer(), nullable=True),
        sa.Column('count_image_click', sa.Integer(), nullable=False),
        sa.Column('count_mouse_movement', sa.Integer(), nullable=False),
        sa.Column('count_read_more_click', sa.Integer(), nullable=False),
        sa.Column('count_through_rate_click', sa.Integer(), nullable=False),
        sa.Column('visit_duration', sa.Integer(), nullable=False),
        sa.Column('validator_block', sa.Integer(), nullable=True),
        sa.Column('validator_hotkey', sa.Integer(), nullable=True),
        sa.Column('refund', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('sales', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('sale_amount', sa.Float(), server_default=sa.text('(0.0)'), nullable=False),
        sa.Column('order_info', sa.PickleType(), nullable=True),
        sa.Column('refund_info', sa.PickleType(), nullable=True),
        sa.Column('sale_date', sa.DateTime(), nullable=True),
        sa.Column('referer', sa.String(), nullable=True),
        sa.Column('campaign_item', sa.String(), nullable=True),
        sa.Column('miner_hotkey', sa.String(), nullable=True),
        sa.Column('miner_block', sa.String(), nullable=True),
        sa.Column('return_in_site', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if not table_exists("campaigns"):
        op.create_table('campaigns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=False),
        sa.Column('last_active_block', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('umax', sa.Float(), nullable=False),
        sa.Column('type', sa.Enum('REGULAR', 'CPA', name='campaigntype'), server_default=sa.text('REGULAR'), nullable=False),
        sa.Column('cpa_blocks', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if not table_exists("miner_assignment"):
        op.create_table('miner_assignment',
        sa.Column('unique_id', sa.String(), nullable=False),
        sa.Column('hotkey', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('unique_id')
        )
    if not table_exists("miner_pings"):
        op.create_table('miner_pings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hot_key', sa.String(), nullable=False),
        sa.Column('block', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    if not table_exists("order_queue"):
        op.create_table('order_queue',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_info', sa.PickleType(), nullable=False),
        sa.Column('refund_info', sa.PickleType(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_processing_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'VISIT_NOT_FOUND', 'PROCESSED', 'ERROR', name='orderqueuestatus'), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    if not table_exists("tracking_data"):
        op.create_table('tracking_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('count_image_click', sa.Integer(), nullable=False),
        sa.Column('count_mouse_movement', sa.Integer(), nullable=False),
        sa.Column('count_read_more_click', sa.Integer(), nullable=False),
        sa.Column('count_through_rate_click', sa.Integer(), nullable=False),
        sa.Column('visit_duration', sa.Integer(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('validator_block', sa.Integer(), nullable=False),
        sa.Column('validator_hotkey', sa.String(), nullable=False),
        sa.Column('at', sa.Boolean(), nullable=False),
        sa.Column('device', sa.Enum('PC', 'MOBILE', name='device'), nullable=True),
        sa.Column('is_unique', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Enum('new', 'synced', 'completed', name='visitstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('refund', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('sales', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('sale_amount', sa.Float(), server_default=sa.text('(0.0)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    # ### end Alembic commands ###


def downgrade_validator_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tracking_data')
    op.drop_table('order_queue')
    op.drop_table('miner_pings')
    op.drop_table('miner_assignment')
    op.drop_table('campaigns')
    op.drop_table('bitads_data')
    # ### end Alembic commands ###


def upgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

