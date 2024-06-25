"""initialization

Revision ID: f887ee30444e
Revises: 
Create Date: 2022-06-22 18:15:07.509492

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f887ee30444e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "premium",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("reaction_roles_amount", sa.SmallInteger(), nullable=False),
        sa.Column("reminders_amount", sa.SmallInteger(), nullable=False),
        sa.Column("reminder_amount_per_user", sa.SmallInteger(), nullable=False),
        sa.Column("no_vote_locked", sa.Boolean(), nullable=False),
        sa.Column("configurable_prefix", sa.Boolean(), nullable=False),
        sa.Column("no_of_servers_applicable", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reaction_roles",
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("server_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("reactions", sa.JSON(), nullable=False),
        sa.Column("limit_to_one", sa.Boolean(), nullable=False),
        sa.Column(
            "custom_id",
            sa.ARRAY(sa.String(length=250), as_tuple=True, zero_indexes=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(
        op.f("ix_reaction_roles_channel_id"),
        "reaction_roles",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reaction_roles_custom_id"),
        "reaction_roles",
        ["custom_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reaction_roles_limit_to_one"),
        "reaction_roles",
        ["limit_to_one"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reaction_roles_message_id"),
        "reaction_roles",
        ["message_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_reaction_roles_server_id"),
        "reaction_roles",
        ["server_id"],
        unique=False,
    )
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expires", sa.DateTime(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reminders_expires"), "reminders", ["expires"], unique=False
    )
    op.create_index(op.f("ix_reminders_id"), "reminders", ["id"], unique=False)
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("premium_id", sa.Integer(), nullable=True),
        sa.Column("premium_expiry", sa.DateTime(), nullable=True),
        sa.Column("blacklisted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["premium_id"],
            ["premium.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "server",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("premium_applier_user_id", sa.Integer(), nullable=True),
        sa.Column("blacklisted", sa.Boolean(), nullable=False),
        sa.Column("show_404_commands_error", sa.Boolean(), nullable=False),
        sa.Column("prefix", sa.String(length=5), nullable=True),
        sa.ForeignKeyConstraint(
            ["premium_applier_user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("server")
    op.drop_table("user")
    op.drop_index(op.f("ix_reminders_id"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_expires"), table_name="reminders")
    op.drop_table("reminders")
    op.drop_index(op.f("ix_reaction_roles_server_id"), table_name="reaction_roles")
    op.drop_index(op.f("ix_reaction_roles_message_id"), table_name="reaction_roles")
    op.drop_index(op.f("ix_reaction_roles_limit_to_one"), table_name="reaction_roles")
    op.drop_index(op.f("ix_reaction_roles_custom_id"), table_name="reaction_roles")
    op.drop_index(op.f("ix_reaction_roles_channel_id"), table_name="reaction_roles")
    op.drop_table("reaction_roles")
    op.drop_table("premium")
    # ### end Alembic commands ###
