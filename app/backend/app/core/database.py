from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    from app.modules.auth.models import User
    from app.modules.chat.models import ChatConversation, ChatMessage
    from app.modules.implements.models import Implement
    from app.modules.recommendations.models import Recommendation
    from app.modules.tractors.models import Tractor

    _ = (User, ChatConversation, ChatMessage, Implement, Recommendation, Tractor)
    Base.metadata.create_all(bind=engine)
