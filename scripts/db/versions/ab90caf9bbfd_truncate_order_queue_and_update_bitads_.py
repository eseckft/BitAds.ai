"""truncate_order_queue_and_update_bitads_data

Revision ID: ab90caf9bbfd
Revises: b4315e291669
Create Date: 2025-04-02 17:17:26.522252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab90caf9bbfd'
down_revision: Union[str, None] = 'b4315e291669'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_miner_active_engine() -> None:
    pass


def downgrade_miner_active_engine() -> None:
    pass


def upgrade_validator_active_engine() -> None:
    # Truncate OrderQueue table
    op.execute('DELETE FROM order_queue')
    
    # Update BitAdsData rows older than 1 month
    op.execute("""
        UPDATE bitads_data 
        SET sales = 0,
            sale_amount = 0,
            refund = 0,
            order_info = NULL,
            refund_info = NULL,
            updated_at = datetime('now'),
            sales_status = 'NEW'
        WHERE sale_date > datetime('now', '-1 month')
    """)


def downgrade_validator_active_engine() -> None:
    # Cannot restore deleted data, but we can add a comment explaining this
    op.execute("""
        -- Note: Cannot restore deleted OrderQueue data or reset BitAdsData values
        -- as the original data is permanently lost and can be accessed by Shopify source provider
    """)


def upgrade_miner_history_engine() -> None:
    pass


def downgrade_miner_history_engine() -> None:
    pass


def upgrade_validator_history_engine() -> None:
    pass


def downgrade_validator_history_engine() -> None:
    pass


def upgrade_main_engine() -> None:
    pass


def downgrade_main_engine() -> None:
    pass

