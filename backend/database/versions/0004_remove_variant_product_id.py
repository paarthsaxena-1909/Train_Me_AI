"""Remove the obsolete product-to-variant back-reference."""

from alembic import op


revision = "0004_remove_variant_product_id"
down_revision = "0003_simple_catalogue"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF EXISTS keeps upgrades safe for fresh databases where 0003 never
    # created the temporary column.
    op.execute('ALTER TABLE product_variants DROP COLUMN IF EXISTS product_id')


def downgrade() -> None:
    op.execute('ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS product_id INTEGER')
