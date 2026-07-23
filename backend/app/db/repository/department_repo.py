from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from db.models.department import Department


class EmployeeRepository:
    """数据访问层，执行 SQL 查询 department 表"""

    @classmethod
    async def get_department(
        cls, session: AsyncSession, department_id: int
    ) -> Optional[Department]:
        """
        按部门id查询部门信息
        Args:
            session: 数据库会话
            department_id: 部门id
        Returns:
            Optional[Department]: 部门信息
        """
        result = await session.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalars().first()

    @classmethod
    async def get_all_departments(cls, session: AsyncSession) -> Optional[Department]:
        """
        查询所有部门
        """
        result = await session.execute(select(Department))
        return result.scalars().all()
