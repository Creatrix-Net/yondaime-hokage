\"\"\"Add bank and giveaways models

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-08-31 10:44:00.000000

\"\"\"
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Bank Account
    op.create_table('bank_accounts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('guild_id', sa.BigInteger(), nullable=True),
    sa.Column('balance', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_guild_id'), 'bank_accounts', ['guild_id'], unique=False)
    op.create_index(op.f('ix_bank_accounts_user_id'), 'bank_accounts', ['user_id'], unique=False)

    # Giveaways
    op.create_table('giveaways',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('message_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.Column('guild_id', sa.BigInteger(), nullable=False),
    sa.Column('host_id', sa.BigInteger(), nullable=False),
    sa.Column('prize', sa.String(length=500), nullable=False),
    sa.Column('winners_count', sa.Integer(), nullable=False),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ended', sa.Boolean(), nullable=False),
    sa.Column('requirements', sa.JSON(), nullable=False),
    sa.Column('weights', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_giveaways_ends_at'), 'giveaways', ['ends_at'], unique=False)
    op.create_index(op.f('ix_giveaways_ended'), 'giveaways', ['ended'], unique=False)
    op.create_index(op.f('ix_giveaways_message_id'), 'giveaways', ['message_id'], unique=True)

    # Giveaway Entries
    op.create_table('giveaway_entries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('giveaway_message_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('entries', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['giveaway_message_id'], ['giveaways.message_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_giveaway_entries_giveaway_message_id'), 'giveaway_entries', ['giveaway_message_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_giveaway_entries_giveaway_message_id'), table_name='giveaway_entries')
    op.drop_table('giveaway_entries')
    
    op.drop_index(op.f('ix_giveaways_message_id'), table_name='giveaways')
    op.drop_index(op.f('ix_giveaways_ended'), table_name='giveaways')
    op.drop_index(op.f('ix_giveaways_ends_at'), table_name='giveaways')
    op.drop_table('giveaways')
    
    op.drop_index(op.f('ix_bank_accounts_user_id'), table_name='bank_accounts')
    op.drop_index(op.f('ix_bank_accounts_guild_id'), table_name='bank_accounts')
    op.drop_table('bank_accounts')
