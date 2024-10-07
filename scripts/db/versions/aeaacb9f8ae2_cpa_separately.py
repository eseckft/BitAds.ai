"""cpa separately

Revision ID: aeaacb9f8ae2
Revises: 7012af2f8da4
Create Date: 2024-10-07 15:49:26.407464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeaacb9f8ae2'
down_revision: Union[str, None] = '7012af2f8da4'
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
    op.add_column('campaigns', sa.Column('cpa_blocks', sa.Integer(), nullable=True))
    op.add_column('miner_assignment', sa.Column('campaign_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade_validator_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('miner_assignment', 'campaign_id')
    op.drop_column('campaigns', 'cpa_blocks')
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
    pass
    # ### end Alembic commands ###


def downgrade_main_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

