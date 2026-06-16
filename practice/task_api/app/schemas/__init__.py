from pydantic import BaseModel, validator
from enum import Enum

class TaskStatus(str,Enum):
    COMPLETED="completed"
    TODO="todo"
    DONE="done"
    
class TaskPriority(str,Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    
class TaskCreate(BaseModel):
    
    title:str
    description:str
    priority:TaskPriority
    
    @validator('title')
    def check_title(cls,v):
        if not v.isalpha():
            raise ValueError("title must contain only letter")
        return v.upper()
    
class TaskResponse(BaseModel):
    id:int
    title:str
    description:str
    status:TaskPriority
    priority:TaskStatus
    
    class Config:
        from_attributes=True