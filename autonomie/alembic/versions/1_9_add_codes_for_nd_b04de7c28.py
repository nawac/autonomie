"""1.9 : add_codes_for_ndf_export

Revision ID: b04de7c28
Revises: 1ca3a6ef9c9d
Create Date: 2014-04-03 16:25:24.109529

"""

# revision identifiers, used by Alembic.
revision = 'b04de7c28'
down_revision = '1ca3a6ef9c9d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    col = sa.Column("compte_tiers", sa.String(30), default="")
    op.add_column("company", col)

    for name in ('code_tva', 'compte_tva'):
        col = sa.Column(name, sa.String(15), default="")
        op.add_column("expense_type", col)

    col = sa.Column("contribution", sa.Boolean(), default=False)
    op.add_column("expense_type", col)


def downgrade():
    op.drop_column('company', "compte_tiers")
    for col in ('code_tva', 'compte_tva', 'contribution'):
        op.drop_column('expense_type', col)