"""add timezone to timestamps

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla users
    op.alter_column('users','created_at', type_=sa.DateTime(timezone=True), postgresql_using='created_at::timestamptz',)
    op.alter_column('users','updated_at', type_=sa.DateTime(timezone=True), postgresql_using='updated_at::timestamptz',)

    # Tabla password_reset_tokens
    op.alter_column('password_reset_tokens','created_at', type_=sa.DateTime(timezone=True), postgresql_using='created_at::timestamptz',)
    op.alter_column(
        'password_reset_tokens',
        'updated_at',
        type_=sa.DateTime(timezone=True),
        postgresql_using='updated_at::timestamptz',
    )
    op.alter_column(
        'password_reset_tokens',
        'expires_at',
        type_=sa.DateTime(timezone=True),
        postgresql_using='expires_at::timestamptz',
    )
    op.alter_column(
        'password_reset_tokens',
        'used_at',
        type_=sa.DateTime(timezone=True),
        postgresql_using='used_at::timestamptz',
    )


def downgrade() -> None:
    # Tabla users
    op.alter_column(
        'users',
        'created_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='created_at::timestamp',
    )
    op.alter_column(
        'users',
        'updated_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='updated_at::timestamp',
    )

    # Tabla password_reset_tokens
    op.alter_column(
        'password_reset_tokens',
        'created_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='created_at::timestamp',
    )
    op.alter_column(
        'password_reset_tokens',
        'updated_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='updated_at::timestamp',
    )
    op.alter_column(
        'password_reset_tokens',
        'expires_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='expires_at::timestamp',
    )
    op.alter_column(
        'password_reset_tokens',
        'used_at',
        type_=sa.DateTime(timezone=False),
        postgresql_using='used_at::timestamp',
    )