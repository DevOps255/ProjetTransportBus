from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
AsyncSession,
async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_table() -> None:

    import asyncio
    from sqlalchemy import event

    async def _create():
        async with engine.begin() as conn:
            await  conn.run_sync(SQLModel.metadata.create_all)

    asyncio.run(_create())

#Si votre choix se porte sur sqlite
async def create_mod()-> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    