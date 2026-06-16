from apis.task_api.app.database import Base
from sqlalchemy import Column, Integer,String,Float,DateTime
from sqlalchemy.sql import func

class Task(Base):
    __tablename__="tasks"
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String, nullable=False)
    description=Column(String, nullable=False)
    status=Column(String, nullable=False)
    priority=Column(String, nullable=False)
    created_at=Column(DateTime, default=func.now())
    updated_at=Column(DateTime,server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"Task(id={Task.id} title={Task.title} description={Task.description} status={Task.status} )"