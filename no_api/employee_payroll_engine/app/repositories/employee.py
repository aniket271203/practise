from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Employee
from app.schemas import EmployeeCreate
from sqlalchemy import select,case, func
from sqlalchemy.orm import selectinload,joinedload

class EmployeeRepository:
    async def create_employee(self,db:AsyncSession,payroll_data:EmployeeCreate)->Employee:
        pass
     
    async def get_for_update(self,db:AsyncSession,employee_id:int)->Employee:
        result=await db.execute(select(Employee)
                                .filter(Employee.id==employee_id)
                                .with_for_update())
        
        return result.scalar_one_or_none()

    async def get_top_5_employees(self,db:AsyncSession):
        result=await db.execute(select(Employee)
                               .order_by(Employee.salary.desc())
                               .limit(5)                               
        )
        return result.scalars().all()
    async def get_employees_above_avg_salary(self,db:AsyncSession):
        avg_salary_subquery=(select(func.avg(Employee.salary)).scalar_subquery())
        
        result=await db.execute(select(Employee)
                                .where(Employee.salary>avg_salary_subquery)
        )
        return result.scalars().all()
    
    async def get_payrolls(self,db:AsyncSession,employee_id:int):
        result=await db.execute(select(Employee)
                                .options(selectinload(Employee.payrolls))
                                .where(Employee.id==employee_id))
        return result.scalars().all()
        
employee_repository=EmployeeRepository()