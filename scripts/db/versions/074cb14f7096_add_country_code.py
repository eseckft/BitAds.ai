"""add country code

Revision ID: 074cb14f7096
Revises: 0c7087028d8c
Create Date: 2024-08-16 19:57:12.888887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '074cb14f7096'
down_revision: Union[str, None] = '0c7087028d8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('visitors', sa.Column('country_code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade_miner_active_engine() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('visitors', 'country_code')
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
