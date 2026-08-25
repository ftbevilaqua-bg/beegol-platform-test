import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.core.database import get_db
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
)
from app.user import repository as profile_repository
from app.user.schemas import ProfileCreate, ProfileUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: ProfileCreate, db: Session = Depends(get_db)):
    if profile_repository.get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A profile with this email already exists",
        )
    user = profile_repository.create_user(db, payload)
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = profile_repository.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh-token", response_model=AccessTokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise invalid_token_exception from exc

    if decoded.get("type") != TokenType.REFRESH.value:
        raise invalid_token_exception

    user_id = decoded.get("sub")
    user = profile_repository.get_user_by_id(db, int(user_id)) if user_id else None
    if not user:
        raise invalid_token_exception

    return AccessTokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = profile_repository.get_user_by_email(db, payload.email)
    if user:
        reset_token = create_reset_token(str(user.id))
        # No email provider is wired up yet, so the reset token is logged here
        # in place of actually sending it to the user's inbox.
        logger.info("Password reset token for %s: %s", user.email, reset_token)

    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )

    try:
        decoded = decode_token(payload.token)
    except ValueError as exc:
        raise invalid_token_exception from exc

    if decoded.get("type") != TokenType.RESET.value:
        raise invalid_token_exception

    user_id = decoded.get("sub")
    user = profile_repository.get_user_by_id(db, int(user_id)) if user_id else None
    if not user:
        raise invalid_token_exception

    profile_repository.update_user(db, user, ProfileUpdate(password=payload.new_password))
    return MessageResponse(message="Password has been reset successfully.")
