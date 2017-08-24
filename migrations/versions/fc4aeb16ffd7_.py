"""empty message

Revision ID: fc4aeb16ffd7
Revises: ab571115b3fa
Create Date: 2017-08-21 22:18:33.070273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc4aeb16ffd7'
down_revision = 'ab571115b3fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bucketlist_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.Column('belongs_to', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['belongs_to'], ['bucketlists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bucketlist_items')
    # ### end Alembic commands ###
