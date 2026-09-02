from datetime import datetime, timezone

from sqlalchemy.orm import Session

from server.core.security import hash_password, verify_password
from server.profile.schemas import ProfileCreate, ProfileUpdate
from server.users.models import User


def get_user_by_email(db: Session, email: str, *, include_deleted: bool = False) -> User | None:
    query = db.query(User).filter(User.email == email)
    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))
    return query.first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def list_users(db: Session) -> list[User]:
    return db.query(User).filter(User.deleted_at.is_(None)).order_by(User.id).all()


def create_user(db: Session, profile: ProfileCreate) -> User:
    user = User(
        name=profile.name,
        email=profile.email,
        password_hash=hash_password(profile.password),
        active=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, updates: ProfileUpdate) -> User:
    if updates.name is not None:
        user.name = updates.name
    if updates.email is not None:
        user.email = updates.email
    if updates.password is not None:
        user.password_hash = hash_password(updates.password)
    if updates.active is not None:
        user.active = updates.active
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
