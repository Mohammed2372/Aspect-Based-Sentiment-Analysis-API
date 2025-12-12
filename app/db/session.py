from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# check on sqlite
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
# factory we use to create db sessions
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
