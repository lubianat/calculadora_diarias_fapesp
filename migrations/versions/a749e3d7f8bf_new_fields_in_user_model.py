"""new fields in user model

Revision ID: a749e3d7f8bf
Revises: b18b3b0c9874
Create Date: 2023-03-13 09:13:05.479603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a749e3d7f8bf'
down_revision = 'b18b3b0c9874'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_number', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('cpf_number', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('address_number', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('address_complement', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('neighbourhood', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('state', sa.String(length=140), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('state')
        batch_op.drop_column('city')
        batch_op.drop_column('neighbourhood')
        batch_op.drop_column('address_complement')
        batch_op.drop_column('address_number')
        batch_op.drop_column('cpf_number')
        batch_op.drop_column('id_number')

    # ### end Alembic commands ###
