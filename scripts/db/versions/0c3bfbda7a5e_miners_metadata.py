"""miners metadata

Revision ID: 0c3bfbda7a5e
Revises: b94ad6beeba4
Create Date: 2025-01-23 20:16:40.656121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c3bfbda7a5e'
down_revision: Union[str, None] = 'b94ad6beeba4'
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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('miners_metadata',
    sa.Column('hotkey', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_offset', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('hotkey')
    )
    # ### end Alembic commands ###


def downgrade_validator_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('miners_metadata')
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
    op.create_table('miners_metadata',
    sa.Column('hotkey', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_offset', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('hotkey')
    )
    # ### end Alembic commands ###


def downgrade_validator_history_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('miners_metadata')
    # ### end Alembic commands ###


def upgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
