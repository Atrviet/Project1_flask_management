"""Create task_log table

Revision ID: 604db95537f6
Revises: 9636fd214eef
Create Date: 2025-04-24 10:32:12.390233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '604db95537f6'
down_revision = '9636fd214eef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('progress', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_log')
    # ### end Alembic commands ###
