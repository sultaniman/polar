"""issue_references

Revision ID: 79c64025f7cf
Revises: 8a14e99b6079
Create Date: 2023-03-21 14:06:04.020963

"""
from alembic import op
import sqlalchemy as sa


# Polar Custom Imports

# revision identifiers, used by Alembic.
revision = "79c64025f7cf"
down_revision = "8a14e99b6079"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "issue_references",
        sa.Column("issue_id", sa.UUID(), nullable=False),
        sa.Column("pull_request_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["issue_id"],
            ["issues.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pull_request_id"],
            ["pull_requests.id"],
        ),
        sa.PrimaryKeyConstraint("issue_id", "pull_request_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("issue_references")
    # ### end Alembic commands ###