from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from db.models.employee import Employee


class EmployeeRepository:
    """数据访问层，执行 SQL 查询 employee 表"""

    @classmethod
    async def get_employee(
        cls, session: AsyncSession, employee_id: int
    ) -> Optional[Employee]:
        """
        按员工id查询员工信息
        Args:
            session: 数据库会话
            employee_id: 员工id
        Returns:
            Optional[Employee]: 员工信息
        """
        result = await session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalars().first()

    @classmethod
    async def get_employee_by_name(
        cls, session: AsyncSession, name: str
    ) -> Optional[Employee]:
        """
        按姓名查员工（oa_tools.get_user_info 调用）
        等价 SQL: SELECT * FROM employee WHERE name = 'jack'
        数据源: backend/resource/database.db
        """
        result = await session.execute(select(Employee).where(Employee.name == name))
        return result.scalars().first()
