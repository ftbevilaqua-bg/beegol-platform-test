from collections.abc import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from server.core.config import dsn_async, settings

connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
}

if settings.db_ssl:
    connect_args["ssl"] = "require"

engine = create_async_engine(
    dsn_async(settings.database_url),
    poolclass=NullPool,
    connect_args=connect_args,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as sessao:
        yield sessao

