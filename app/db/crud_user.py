from sqlalchemy.orm import session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def create_user(db: session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
