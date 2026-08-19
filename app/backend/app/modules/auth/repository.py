from __future__ import annotations

from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.auth.models import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, name: str, email: str, cpf: str, password_hash: str) -> User:
        user = User(name=name, email=email, cpf=cpf, password_hash=password_hash, role="admin" if self.count_users() == 0 else "user")
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_cpf(self, cpf: str) -> User | None:
        return self.db.scalar(select(User).where(User.cpf == cpf))

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def count_users(self) -> int:
        return int(self.db.scalar(select(func.count(User.id))) or 0)
