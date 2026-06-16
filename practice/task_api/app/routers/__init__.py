from fastapi import APIRouter, Depends
from apis.task_api.app.ratelimiter import check_rate_limit
from apis.task_api.app.auth import verify_api_key
from apis.task_api.app.services import task_services
from apis.task_api.app.schemas import TaskCreate, TaskPriority, TaskResponse, TaskStatus
from apis.task_api.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

router=APIRouter(prefix="/tasks",tags=["tasks"],dependencies=[Depends(check_rate_limit),Depends(verify_api_key)])

@router.post('/', response_model=TaskResponse, status_code=201)
async def create_task(task_data:TaskCreate, db:AsyncSession=Depends(get_db)):
    return await task_services.create_task(db,task_data)

@router.get('/{id}', response_model=TaskResponse)
async def get_task_by_id(id:int, db:AsyncSession=Depends(get_db)):
    return await task_services.get_task_by_id(db,id)

@router.get('/', response_model=List[TaskResponse])
async def get_tasks(skip:int=0,limit:int=10, db:AsyncSession=Depends(get_db)):
    if limit>100:
        limit=100
    return await task_services.get_tasks(db, skip,limit)

@router.patch('/{id}', response_model=TaskResponse)
async def update_task(id:int,status:TaskStatus, db:AsyncSession=Depends(get_db)):
    return await task_services.update_task(db,id,status)

@router.delete('/{id}', response_model=TaskResponse)
async def delete_task(id:int, db:AsyncSession=Depends(get_db)):
    return await task_services.delete_task(db,id)

