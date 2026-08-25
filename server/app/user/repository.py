from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.user.models import User
from app.user.schemas import ProfileCreate, ProfileUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def create_user(db: Session, profile: ProfileCreate) -> User:
    user = User(
        nome=profile.nome,
        email=profile.email,
        password_hash=hash_password(profile.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, updates: ProfileUpdate) -> User:
    if updates.nome is not None:
        user.nome = updates.nome
    if updates.email is not None:
        user.email = updates.email
    if updates.password is not None:
        user.password_hash = hash_password(updates.password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
