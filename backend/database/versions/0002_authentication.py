"""Store password hashes and geographic pincode data for authentication."""

import sqlalchemy as sa
from alembic import op


revision = "0002_authentication"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "agents",
        "password",
        existing_type=sa.String(length=255),
        existing_nullable=False,
        new_column_name="password_hash",
    )
    op.alter_column(
        "admins",
        "password",
        existing_type=sa.String(length=255),
        existing_nullable=False,
        new_column_name="password_hash",
    )
    # Legacy agents have no captured geographic data. Keep those rows NULL;
    # new signup requests provide a validated six-digit value.
    op.add_column("agents", sa.Column("pincode", sa.String(length=6), nullable=True))
    op.create_check_constraint(
        "ck_agents_pincode_six_digits",
        "agents",
        "pincode IS NULL OR pincode ~ '^[0-9]{6}$'",
    )


def downgrade() -> None:
    op.drop_constraint("ck_agents_pincode_six_digits", "agents", type_="check")
    op.drop_column("agents", "pincode")
    op.alter_column(
        "admins",
        "password_hash",
        existing_type=sa.String(length=255),
        existing_nullable=False,
        new_column_name="password",
    )
    op.alter_column(
        "agents",
        "password_hash",
        existing_type=sa.String(length=255),
        existing_nullable=False,
        new_column_name="password",
    )
