from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.database import get_session
from server.core.dependencies import get_current_user
from server.users import repository
from server.users.models import User
from server.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/auth/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=ProfileOut)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if payload.email is not None:
        existing = await repository.get_user_by_email(db, payload.email, include_deleted=True)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A profile with this email already exists",
            )
    return await repository.update_user(db, current_user, payload)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await repository.delete_user(db, current_user)
