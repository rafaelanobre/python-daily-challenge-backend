from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Challenge(Base):
    __tablename__ = 'challenges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    difficulty = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    created_by = Column(String, nullable=False)
    title = Column(String, nullable=False)
    options = Column(String, nullable=False)
    correct_answer_id = Column(Integer, nullable=False)
    explanation = Column(String, nullable=False)

class ChallengeQuota(Base):
    __tablename__ = 'challenge_quotas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, unique=True)
    quota_remaining = Column(Integer, nullable=False, default=50)
    last_reset_date = Column(DateTime, default=datetime.now)

def get_engine():
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required.")

    return create_engine(
        database_url,
        echo=True,
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10
        }
    )

def get_db():
    engine = get_engine()
    session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    db = session_local()
    try:
        yield db
    finally:
        db.close()