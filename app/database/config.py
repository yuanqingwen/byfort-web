from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import os

DATABASE_URL = os.getenv('DATABASE_URL','sqlite+aiosqlite:///./byfort.db')
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.orm import sessionmaker

async_session = sessionmaker(engine, class_=_AsyncSession, expire_on_commit=False)

def get_session():
    return async_session()
