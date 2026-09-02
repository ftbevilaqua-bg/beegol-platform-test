from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.dependencies import get_current_user
from server.users import repository
from server.users.models import User
from server.profile.schemas import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/auth/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def read_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.email is not None:
        existing = repository.get_user_by_email(db, payload.email, include_deleted=True)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A profile with this email already exists",
            )
    return repository.update_user(db, current_user, payload)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository.delete_user(db, current_user)
