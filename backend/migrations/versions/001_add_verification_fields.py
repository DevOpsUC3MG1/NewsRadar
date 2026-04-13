"""Add verification fields to users table

Revision ID: 001_add_verification_fields
Revises: 
Create Date: 2026-04-12 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001_add_verification_fields"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("verification_token", sa.String(128), nullable=True),
    )
    
    # Create index for faster lookups
    op.create_index(
        op.f("ix_users_verification_token"),
        "users",
        ["verification_token"],
        unique=False,
    )


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f("ix_users_verification_token"), table_name="users")
    
    # Drop columns
    op.drop_column("users", "verification_token")
    op.drop_column("users", "is_verified")
