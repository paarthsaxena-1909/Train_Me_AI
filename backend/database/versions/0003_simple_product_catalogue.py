"""Migrate the legacy lineup model to the simple product catalogue."""
import sqlalchemy as sa
from alembic import op

revision = "0003_simple_catalogue"
down_revision = "0002_authentication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("name", sa.String(255), nullable=True))
    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("product_variants", sa.Column("name", sa.String(255), nullable=True))
    op.execute("UPDATE products SET name = 'Legacy product ' || _id WHERE name IS NULL")
    op.execute("UPDATE product_variants SET name = 'Legacy variant ' || _id WHERE name IS NULL")
    op.alter_column("products", "name", nullable=False)
    op.alter_column("product_variants", "name", nullable=False)
    op.alter_column("product_variants", "product_lineup_id", nullable=True)
    op.alter_column("products", "product_lineup_id", nullable=True)
    op.alter_column("products", "product_variant_id", nullable=True)


def downgrade() -> None:
    op.execute('DELETE FROM product_variants WHERE product_lineup_id IS NULL')
    op.execute('DELETE FROM products WHERE product_lineup_id IS NULL OR product_variant_id IS NULL')
    op.alter_column("products", "product_variant_id", nullable=False)
    op.alter_column("products", "product_lineup_id", nullable=False)
    op.alter_column("product_variants", "product_lineup_id", nullable=False)
    op.drop_column("product_variants", "name")
    op.drop_column("products", "description")
    op.drop_column("products", "name")
