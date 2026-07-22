"""
数据库连接配置
.env: DATABASE_URL=sqlite+aiosqlite:///resource/database.db
从 backend/ 目录启动时 → backend/resource/database.db
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator

from core.config import settings
from functools import wraps
from typing import Annotated
from fastapi import Depends
import os


# 创建异步引擎，连接 SQLite（员工/部门业务数据）
async_engine = create_async_engine(settings.DATABASE_URL)

# 异步 Session 工厂，oa_tools.py 通过 async_session_maker() 获取连接
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

# sessionmaker = sessionmaker(
#     engine, expire_on_commit=False, class_=Session
# )

# def get_seesion():
#     with sessionmaker() as session:
#         yield session


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# create_db_and_tables();


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def db_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with async_session_maker() as session:
            try:
                result = f(session, *args, **kwargs)
                session.commit()
                return result
            except:
                session.rollback()
                raise

    return wrapper
