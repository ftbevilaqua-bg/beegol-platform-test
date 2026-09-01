import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_from_refresh_token, get_user_from_reset_token
from app.auth.schemas import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    TokenResponse,
)
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, create_reset_token
from app.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from app.users import repository as profile_repository
from app.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def register(payload: ProfileCreate, db: Session = Depends(get_db)):
    if profile_repository.get_user_by_email(db, payload.email, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A profile with this email already exists",
        )
    return profile_repository.create_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = profile_repository.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact an administrator.",
        )
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh-token", response_model=AccessTokenResponse)
def refresh_token(user: User = Depends(get_user_from_refresh_token)):
    return AccessTokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = profile_repository.get_user_by_email(db, payload.email)
    if user:
        reset_token = create_reset_token(str(user.id))
        logger.info("Password reset token for %s: %s", user.email, reset_token)

    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    resolved: tuple[User, str] = Depends(get_user_from_reset_token),
    db: Session = Depends(get_db),
):
    user, new_password = resolved
    profile_repository.update_user(db, user, ProfileUpdate(password=new_password))
    return MessageResponse(message="Password has been reset successfully.")
