from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.database import get_session
from server.core.dependencies import get_current_user
from server.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from server.users import repository
from server.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


async def _get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: ProfileCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    if await repository.get_user_by_email(db, payload.email, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    return await repository.create_user(db, payload)


@router.get("", response_model=list[ProfileOut])
async def list_users(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await repository.list_users(db)


@router.get("/{user_id}", response_model=ProfileOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await _get_user_or_404(db, user_id)


@router.put("/{user_id}", response_model=ProfileOut)
async def update_user(
    user_id: int,
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    user = await _get_user_or_404(db, user_id)
    if payload.email is not None:
        existing = await repository.get_user_by_email(db, payload.email, include_deleted=True)
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
    return await repository.update_user(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    user = await _get_user_or_404(db, user_id)
    await repository.delete_user(db, user)
