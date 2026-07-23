from dataclasses import dataclass
from sqlmodel import Field
from db.models.base import DBBaseModel


@dataclass
class Department(DBBaseModel, table=True):
    """
    department model
    """

    __tablename__ = "department"
    id: int = Field(primary_key=True, index=True, description="部门ID")
    name: str = Field(max_length=50, index=True, description="部门名称")
    parent_id: int = Field(default=0, description="父部门ID")
    manager_id: int = Field(default=0, description="部门负责人 ID")
