from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.dependencies import get_current_user
from server.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from server.users import repository
from server.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: ProfileCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if repository.get_user_by_email(db, payload.email, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    return repository.create_user(db, payload)


@router.get("", response_model=list[ProfileOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return repository.list_users(db)


@router.get("/{user_id}", response_model=ProfileOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_user_or_404(db, user_id)


@router.put("/{user_id}", response_model=ProfileOut)
def update_user(
    user_id: int,
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = _get_user_or_404(db, user_id)
    if payload.email is not None:
        existing = repository.get_user_by_email(db, payload.email, include_deleted=True)
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
    return repository.update_user(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = _get_user_or_404(db, user_id)
    repository.delete_user(db, user)
