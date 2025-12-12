from sqlalchemy.orm import declarative_base

Base = declarative_base()

# import all models, so Alembic can find them
from app.models.user import User  # noqa
from app.models.analysis import AnalysisSession, AnalysisRecord, AspectResult  # noqa
