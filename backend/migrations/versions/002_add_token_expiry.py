"""Add verification_token_expires_at to users

Revision ID: 002_add_token_expiry
Revises: 001_add_verification_fields
Create Date: 2026-05-24 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_add_token_expiry"
down_revision = "001_add_verification_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("verification_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "verification_token_expires_at")
