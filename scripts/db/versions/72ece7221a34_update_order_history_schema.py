"""update_order_history_schema

Revision ID: 72ece7221a34
Revises: 7c118bdeca6d
Create Date: 2024-12-03 17:53:57.975164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72ece7221a34"
down_revision: Union[str, None] = "7c118bdeca6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def upgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_validator_active_engine() -> None:
    op.execute("UPDATE order_queue SET status = 'PENDING'")


def downgrade_validator_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_miner_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_miner_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_validator_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_validator_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def upgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "miner_order_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_processing_date", sa.DateTime(), nullable=False),
        sa.Column("hotkey", sa.String(), nullable=False),
        sa.Column("data", sa.PickleType(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NEW", "ORDER", "REFUND", "ERROR", name="ordernotificationstatus"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("miner_order_history")
    # ### end Alembic commands ###
