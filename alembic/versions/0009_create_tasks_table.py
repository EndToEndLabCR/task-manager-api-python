"""create tasks table

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-02 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '0009'
down_revision: Union[str, None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, unique=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='todo'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('source_note_id', UUID(as_uuid=True), sa.ForeignKey('notes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('tasks')
