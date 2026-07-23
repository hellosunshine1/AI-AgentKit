"""
数据库连接与会话配置模块。

职责：
1. 根据 `settings.DATABASE_URL` 创建异步数据库引擎。
2. 提供统一的 `AsyncSession` 工厂，供 API 层、工具层和仓储层复用。
3. 提供建表入口、FastAPI 依赖注入以及装饰器式事务封装，避免各处重复编写会话管理逻辑。

核心依赖：
- `core.config.settings`：提供数据库连接字符串。
- `SQLModel`：用于根据模型元数据创建数据库表。
- `sqlalchemy.ext.asyncio`：提供异步引擎与异步会话支持。
- `fastapi.Depends`：将数据库会话注入到 FastAPI 路由中。
"""

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator

from core.config import settings
from functools import wraps
from typing import Annotated
from fastapi import Depends


# 使用异步引擎是为了让数据库 I/O 不阻塞事件循环，提升 FastAPI 的并发吞吐能力。
async_engine = create_async_engine(settings.DATABASE_URL)

# 将引擎封装成统一的 Session 工厂，便于在不同模块中按需创建短生命周期会话。
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def create_db_and_tables():
    """创建数据库中 SQLModel 定义的所有表。

    Args:
        无。

    Returns:
        None：通过异步连接执行建表操作，结果体现在数据库侧。
    """
    async with async_engine.begin() as conn:
        # 通过统一元数据建表，确保模型与数据库结构保持一致。
        await conn.run_sync(SQLModel.metadata.create_all)


# 启动时按需调用，可避免在导入阶段直接执行建表导致副作用过早发生。
# create_db_and_tables();


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """为 FastAPI 依赖注入提供一个异步数据库会话。

    Args:
        无。

    Yields:
        AsyncSession：一个在请求生命周期内可复用的数据库会话。
    """
    async with async_session_maker() as session:
        # 使用生成器依赖可以让 FastAPI 在请求结束后自动清理会话资源。
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def db_session(f):
    """为同步函数提供装饰器式数据库会话与事务管理。

    Args:
        f: 需要接收 `session` 作为首个参数的同步函数。

    Returns:
        Callable: 包装后的函数；成功时自动提交事务，异常时自动回滚。
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        with async_session_maker() as session:
            try:
                # 将会话显式传入业务函数，便于统一控制事务边界。
                result = f(session, *args, **kwargs)
                # 显式提交确保写操作在函数成功后落库，避免半成品数据。
                session.commit()
                return result
            except:
                # 出错时回滚，保证事务原子性，防止脏数据写入。
                session.rollback()
                raise

    return wrapper
