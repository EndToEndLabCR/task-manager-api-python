from sqlalchemy import Column, String, JSON, Boolean
from src.shared.infrastructure.models.base_model import BaseModel


class UserModel(BaseModel):
    """SQLAlchemy model for the 'users' table."""

    __tablename__ = 'users'

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False, server_default="false")
    preferences = Column(JSON, nullable=True)
