"""
User Model
==========
Represents a registered SmartRail user.

Key fields:
- email: Unique email address (used for login)
- name: Display name
- password_hash: bcrypt-hashed password (never store plaintext!)
- created_at / updated_at: Timestamps for auditing
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from app.database.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Display name
    name = Column(String(100), nullable=False)

    # Email — unique identifier for login
    email = Column(String(255), unique=True, nullable=False, index=True)

    # bcrypt password hash (60 chars for bcrypt)
    password_hash = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_users_email_lower", "email"),
    )

    def __repr__(self) -> str:
        return f"<User {self.id} - {self.email}>"
