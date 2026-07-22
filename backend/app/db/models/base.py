import datetime

from pydantic import Field
from sqlmodel import SQLModel


class DBBaseModel(SQLModel):
    """
    SQLModel 基类，所有模型继承该类
    """

    create_time: datetime | None = Field(default=datetime.now, title="创建时间")
    edit_time: datetime | None = Field(default=datetime.now, title="更新时间")
