from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import AuthResponse, UserCreate, UserLogin, UserRead


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepository(db)

    def register(self, payload: UserCreate) -> AuthResponse:
        if self.repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ja cadastrado")
        if self.repository.get_by_cpf(payload.cpf):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CPF ja cadastrado")
        user = self.repository.create_user(
            name=payload.name,
            email=payload.email,
            cpf=payload.cpf,
            password_hash=hash_password(payload.password),
        )
        self.db.commit()
        return self._auth_response(user)

    def login(self, payload: UserLogin) -> AuthResponse:
        user = self.repository.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha invalidos")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inativo")
        return self._auth_response(user)

    def get_user(self, user_id: int) -> UserRead:
        user = self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")
        return UserRead.model_validate(user)

    def _auth_response(self, user) -> AuthResponse:
        return AuthResponse(access_token=create_access_token(str(user.id)), user=UserRead.model_validate(user))
