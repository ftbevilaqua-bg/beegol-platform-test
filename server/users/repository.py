from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.security import hash_password, verify_password
from server.profile.schemas import ProfileCreate, ProfileUpdate
from server.users.models import User


async def get_user_by_email(db: AsyncSession, email: str, *, include_deleted: bool = False) -> User | None:
    query = select(User).where(User.email == email)
    if not include_deleted:
        query = query.where(User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).where(User.deleted_at.is_(None)).order_by(User.id))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, profile: ProfileCreate) -> User:
    user = User(
        name=profile.name,
        email=profile.email,
        password_hash=hash_password(profile.password),
        active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, updates: ProfileUpdate) -> User:
    if updates.name is not None:
        user.name = updates.name
    if updates.email is not None:
        user.email = updates.email
    if updates.password is not None:
        user.password_hash = hash_password(updates.password)
    if updates.active is not None:
        user.active = updates.active
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    user.deleted_at = datetime.now(timezone.utc)
    await db.commit()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
