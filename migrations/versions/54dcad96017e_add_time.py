"""add time

Revision ID: 54dcad96017e
Revises: 33a824213bbf
Create Date: 2025-07-21 21:17:03.686162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54dcad96017e'
down_revision = '33a824213bbf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('route', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('route', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###
