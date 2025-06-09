"""Database models for the Pomodoro bot."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from app.config import config

# Create SQLAlchemy engine and session
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    pomodoro_sessions = relationship("PomodoroSession", back_populates="user")

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"User(telegram_id={self.telegram_id}, username={self.username})"


class PomodoroSession(Base):
    """Pomodoro session model."""

    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    work_minutes = Column(Integer)
    break_minutes = Column(Integer)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Integer, default=0)  # Number of completed pomodoros

    # Relationship
    user = relationship("User", back_populates="pomodoro_sessions")

    def __repr__(self) -> str:
        """String representation of the PomodoroSession model."""
        return (
            f"PomodoroSession(id={self.id}, "
            f"user_id={self.user_id}, "
            f"completed={self.completed})"
        )


# Create all tables
def init_db():
    """Initialize the database."""
    Base.metadata.create_all(bind=engine) 