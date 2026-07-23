from langchain_core.tools import tool
from db.database import async_session_maker
from db.repository.employee_repo import EmployeeRepository
from db.repository.department_repo import DepartmentRepository
from dataclasses import asdict


@tool
async def get_user_info(user_name: str) -> dict:
    """根据姓名查询员工基本信息。LLM 查 jack 时会调用这个方法"""
    async with async_session_maker() as session:
        employee = await EmployeeRepository.get_employee_by_name(session, user_name)
        if not employee:
            return {"error": "员工不存在"}

        return asdict(employee)


@tool
async def get_user_department(user_name: str) -> dict:
    """根据姓名查询员工所属部门信息"""

    async with async_session_maker() as session:
        employee = await EmployeeRepository.get_employee_by_name(
            session, name=user_name
        )

        if not employee:
            return {"error": "user not found"}

        department = await DepartmentRepository.get_department(
            session, department_id=employee.department_id
        )

        if not department:
            return {"error": "department not found"}

        return asdict(department)
