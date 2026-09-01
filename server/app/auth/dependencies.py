from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import RefreshTokenRequest, ResetPasswordRequest
from app.core.database import get_db
from app.core.security import TokenType, decode_token
from app.users import repository as profile_repository
from app.users.models import User


def get_user_from_refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> User:
    """Resolve and validate a refresh token, returning its owning user.

    Centralizes the decode/type/lookup checks shared by any route that needs
    a valid refresh token, the same way get_current_user centralizes access
    token validation for Bearer-protected routes.
    """
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

    return user


def get_user_from_reset_token(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> tuple[User, str]:
    """Resolve and validate a password-reset token, returning the owning user
    alongside the new password from the same request body.
    """
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

    return user, payload.new_password
