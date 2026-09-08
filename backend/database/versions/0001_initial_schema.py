"""Create the initial Train Me database schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _audit_columns() -> tuple[sa.Column, ...]:
    return (
        sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deletedAt", sa.DateTime(timezone=True), nullable=True),
    )


def _id_column() -> sa.Column:
    return sa.Column("_id", sa.Integer(), primary_key=True, autoincrement=True)


def upgrade() -> None:
    op.create_table(
        "agents",
        _id_column(),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        *_audit_columns(),
        sa.UniqueConstraint("email", name="uq_agents_email"),
    )
    op.create_index("ix_agents_email", "agents", ["email"], unique=False)

    op.create_table(
        "admins",
        _id_column(),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        *_audit_columns(),
        sa.UniqueConstraint("email", name="uq_admins_email"),
    )
    op.create_index("ix_admins_email", "admins", ["email"], unique=False)

    op.create_table(
        "blob_items",
        _id_column(),
        sa.Column("key", sa.String(length=1024), nullable=False),
        sa.Column("bucket", sa.String(length=255), nullable=False),
        *_audit_columns(),
    )

    op.create_table(
        "product_lineups",
        _id_column(),
        sa.Column("lineup_identifier", sa.String(length=255), nullable=False),
        *_audit_columns(),
    )

    op.create_table(
        "product_variants",
        _id_column(),
        sa.Column("specs", sa.Text(), nullable=False),
        sa.Column("product_lineup_id", sa.Integer(), sa.ForeignKey("product_lineups._id", ondelete="CASCADE"), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_product_variants_product_lineup_id", "product_variants", ["product_lineup_id"])

    op.create_table(
        "products",
        _id_column(),
        sa.Column("product_lineup_id", sa.Integer(), sa.ForeignKey("product_lineups._id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_variant_id", sa.Integer(), sa.ForeignKey("product_variants._id", ondelete="CASCADE"), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_products_product_lineup_id", "products", ["product_lineup_id"])
    op.create_index("ix_products_product_variant_id", "products", ["product_variant_id"])

    op.create_table(
        "assignments",
        _id_column(),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        *_audit_columns(),
    )

    op.create_table(
        "assignment_questions",
        _id_column(),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("evaluation", sa.Text(), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products._id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments._id", ondelete="CASCADE"), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_assignment_questions_product_id", "assignment_questions", ["product_id"])
    op.create_index("ix_assignment_questions_assignment_id", "assignment_questions", ["assignment_id"])

    op.create_table(
        "assignment_agent_mapping",
        _id_column(),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents._id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments._id", ondelete="CASCADE"), nullable=False),
        *_audit_columns(),
        sa.UniqueConstraint("agent_id", "assignment_id", name="uq_assignment_agent_mapping_pair"),
    )
    op.create_index("ix_assignment_agent_mapping_agent_id", "assignment_agent_mapping", ["agent_id"])
    op.create_index("ix_assignment_agent_mapping_assignment_id", "assignment_agent_mapping", ["assignment_id"])

    op.create_table(
        "agent_queries",
        _id_column(),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products._id", ondelete="CASCADE"), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_agent_queries_product_id", "agent_queries", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_agent_queries_product_id", table_name="agent_queries")
    op.drop_table("agent_queries")
    op.drop_index("ix_assignment_agent_mapping_assignment_id", table_name="assignment_agent_mapping")
    op.drop_index("ix_assignment_agent_mapping_agent_id", table_name="assignment_agent_mapping")
    op.drop_table("assignment_agent_mapping")
    op.drop_index("ix_assignment_questions_assignment_id", table_name="assignment_questions")
    op.drop_index("ix_assignment_questions_product_id", table_name="assignment_questions")
    op.drop_table("assignment_questions")
    op.drop_table("assignments")
    op.drop_index("ix_products_product_variant_id", table_name="products")
    op.drop_index("ix_products_product_lineup_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_product_variants_product_lineup_id", table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_table("product_lineups")
    op.drop_table("blob_items")
    op.drop_index("ix_admins_email", table_name="admins")
    op.drop_table("admins")
    op.drop_index("ix_agents_email", table_name="agents")
    op.drop_table("agents")
