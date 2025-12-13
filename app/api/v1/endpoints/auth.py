from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db import crud_user
from app.schemas.user import UserCreate, UserResponse, Token


router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    # check if email exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # check if username exists
    if crud_user.get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    # create user
    user = crud_user.create_user(db, user=user_in)
    return user


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # authenticate
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # create JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
