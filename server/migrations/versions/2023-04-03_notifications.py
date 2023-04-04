"""notifications

Revision ID: 4962f5f9e62c
Revises: d67af495a760
Create Date: 2023-04-03 11:30:42.529306

"""
from alembic import op
import sqlalchemy as sa


# Polar Custom Imports

# revision identifiers, used by Alembic.
revision = "4962f5f9e62c"
down_revision = "d67af495a760"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "notifications",
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("issue_id", sa.UUID(), nullable=True),
        sa.Column("pledge_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("notifications_pkey")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("notifications")
    # ### end Alembic commands ###