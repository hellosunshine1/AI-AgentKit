from dataclasses import dataclass

from sqlmodel import Field
from db.models.base import DBBaseModel


@dataclass
class Employee(DBBaseModel, table=True):
    """
    employee model
    """

    __tablename__ = "employee"
    id: int = Field(primary_key=True, index=True, description="员工Id")
    employee_no: str = Field(max_length=50, description="员工编号")
    name: str = Field(max_length=50, index=True, description="员工姓名")
    gender: int = Field(max_length=10, description="性别：0-未知 1-男 2-女")
    department_id: int = Field(default=0, description="部门 ID")
    position: str = Field(max_length=50, description="职位")
    phone: str = Field(max_length=11, description="手机号")
    email: str = Field(max_length=50, description="邮箱")
    status: int = Field(default=0, description="状态：1-试用期 2-在职 3-离职")
    entry_date: str = Field(max_length=50, description="入职日期")
