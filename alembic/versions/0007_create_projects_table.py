"""create projects table

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-31 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the projects table."""
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('github_repo_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
        sa.UniqueConstraint('owner_id', 'name', name='uq_projects_owner_id_name'),
    )


def downgrade() -> None:
    """Drop the projects table."""
    op.drop_table('projects')
