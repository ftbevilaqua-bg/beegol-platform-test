import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.auth.dependencies import get_user_from_refresh_token, get_user_from_reset_token
from server.auth.schemas import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    TokenResponse,
)
from server.core.database import get_session
from server.core.security import create_access_token, create_refresh_token, create_reset_token
from server.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from server.users import repository as profile_repository
from server.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def register(payload: ProfileCreate, db: AsyncSession = Depends(get_session)):
    if await profile_repository.get_user_by_email(db, payload.email, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A profile with this email already exists",
        )
    return await profile_repository.create_user(db, payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_session)):
    user = await profile_repository.authenticate_user(db, payload.email, payload.password)
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
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_session)):
    user = await profile_repository.get_user_by_email(db, payload.email)
    if user:
        reset_token = create_reset_token(str(user.id))
        logger.info("Password reset token for %s: %s", user.email, reset_token)

    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    resolved: tuple[User, str] = Depends(get_user_from_reset_token),
    db: AsyncSession = Depends(get_session),
):
    user, new_password = resolved
    await profile_repository.update_user(db, user, ProfileUpdate(password=new_password))
    return MessageResponse(message="Password has been reset successfully.")
