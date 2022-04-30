"""Initial migration.

Revision ID: 5fd9dcf670c2
Revises: 
Create Date: 2022-04-29 16:12:09.035082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fd9dcf670c2'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aiots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=255), nullable=True),
    sa.Column('numero_voie', sa.Integer(), nullable=True),
    sa.Column('voie', sa.String(length=255), nullable=True),
    sa.Column('code_postal', sa.String(length=255), nullable=True),
    sa.Column('commune', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Text(), nullable=True),
    sa.Column('store_id', sa.Text(), nullable=True),
    sa.Column('store_path', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inspections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('aiot_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=255), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['aiot_id'], ['aiots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('insp_controles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('insp_id', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=True),
    sa.Column('date_source', sa.Date(), nullable=True),
    sa.Column('article_source', sa.String(length=255), nullable=True),
    sa.Column('theme', sa.String(length=255), nullable=True),
    sa.Column('sous_theme', sa.String(length=255), nullable=True),
    sa.Column('prescription', sa.Text(), nullable=True),
    sa.Column('constats', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['insp_id'], ['inspections.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('insp_controles')
    op.drop_table('inspections')
    op.drop_table('users')
    op.drop_table('files')
    op.drop_table('aiots')
    # ### end Alembic commands ###