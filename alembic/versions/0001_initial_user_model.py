"""initial user model

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create the users table with the correct schema."""
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, unique=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('preferences', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, index=True, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop the users table."""
    op.drop_table('users')