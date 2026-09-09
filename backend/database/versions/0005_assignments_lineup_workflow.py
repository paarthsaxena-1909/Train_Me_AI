"""Make assignments belong to lineups and support one-shot evaluation."""
import sqlalchemy as sa
from alembic import op

revision = "0005_assignment_lineup_workflow"
down_revision = "0004_remove_variant_product_id"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("assignments", sa.Column("product_lineup_id", sa.Integer(), nullable=True))
    op.execute("UPDATE assignments SET product_lineup_id = (SELECT _id FROM product_lineups ORDER BY _id LIMIT 1) WHERE product_lineup_id IS NULL")
    op.alter_column("assignments", "product_lineup_id", nullable=False)
    op.create_foreign_key("fk_assignments_product_lineup_id", "assignments", "product_lineups", ["product_lineup_id"], ["_id"], ondelete="CASCADE")
    op.create_index("ix_assignments_product_lineup_id", "assignments", ["product_lineup_id"])
    op.create_index("ix_assignments_status", "assignments", ["status"])
    op.alter_column("assignments", "status", nullable=True)
    op.add_column("assignment_questions", sa.Column("question", sa.Text(), nullable=True))
    op.execute("UPDATE assignment_questions SET question = 'Legacy assignment question ' || question_number WHERE question IS NULL")
    op.alter_column("assignment_questions", "question", nullable=False)
    op.alter_column("assignment_questions", "answer", nullable=True)
    op.alter_column("assignment_questions", "evaluation", nullable=True)
    op.drop_index("ix_assignment_questions_product_id", table_name="assignment_questions")
    op.drop_constraint("assignment_questions_product_id_fkey", "assignment_questions", type_="foreignkey")
    op.drop_column("assignment_questions", "product_id")

def downgrade() -> None:
    op.add_column("assignment_questions", sa.Column("product_id", sa.Integer(), nullable=True))
    op.drop_index("ix_assignments_product_lineup_id", table_name="assignments")
    op.drop_index("ix_assignments_status", table_name="assignments")
    op.drop_constraint("fk_assignments_product_lineup_id", "assignments", type_="foreignkey")
    for column in ("product_lineup_id",):
        op.drop_column("assignments", column)
