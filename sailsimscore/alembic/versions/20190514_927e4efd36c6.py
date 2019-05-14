"""Replace template models

Revision ID: 927e4efd36c6
Revises: 103b836170cc
Create Date: 2019-05-14 17:04:08.726955

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '927e4efd36c6'
down_revision = '103b836170cc'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('boats',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('resource', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_boats'))
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_events'))
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('role', sa.Text(), nullable=False),
    sa.Column('password_hash', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('name', name=op.f('uq_users_name'))
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_comments_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_comments'))
    )
    op.create_table('recordings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Numeric(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.Column('hash', sa.BINARY(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('boat_id', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['boat_id'], ['boats.id'], name=op.f('fk_recordings_boat_id_boats')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_recordings_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recordings'))
    )
    op.create_table('eventrecordings',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('recording_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_eventrecordings_event_id_events')),
    sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], name=op.f('fk_eventrecordings_recording_id_recordings')),
    sa.PrimaryKeyConstraint('event_id', 'recording_id', name=op.f('pk_eventrecordings'))
    )
    op.create_table('reccomments',
    sa.Column('recording_id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.Column('op', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], name=op.f('fk_reccomments_comment_id_comments')),
    sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], name=op.f('fk_reccomments_recording_id_recordings')),
    sa.PrimaryKeyConstraint('recording_id', 'comment_id', name=op.f('pk_reccomments'))
    )
    op.drop_index('my_index', table_name='models')
    op.drop_table('models')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('models',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('value', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_models')
    )
    op.create_index('my_index', 'models', ['name'], unique=1)
    op.drop_table('reccomments')
    op.drop_table('eventrecordings')
    op.drop_table('recordings')
    op.drop_table('comments')
    op.drop_table('users')
    op.drop_table('events')
    op.drop_table('boats')
    # ### end Alembic commands ###
