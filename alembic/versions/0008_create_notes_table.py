"""create notes table

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-02 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = '0008'
down_revision: Union[str, None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, unique=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(30), nullable=False, server_default='raw'),
        sa.Column('is_enriched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ai_suggestion', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('notes')
