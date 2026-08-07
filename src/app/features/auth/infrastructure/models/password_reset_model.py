from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID

from src.shared.infrastructure.models.base_model import BaseModel


class PasswordResetTokenModel(BaseModel):
    __tablename__ = 'password_reset_tokens'

    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)