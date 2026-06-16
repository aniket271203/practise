from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department,Employee
from app.schemas import DepartmentCreate
from sqlalchemy import select,case, func

class DepartmentRepository:
    async def get_department_summary(self,db:AsyncSession):
        result=await db.execute(
                                select(
                                Department.name.label('department'),
                                func.count(Employee.id).label("employee_count"),
                                func.sum(Employee.salary).label("total_salary"))
                                .select_from(Department)
                                .join(Employee,Employee.department_id==Department.id)
                                .group_by(Department.id,Department.name)          
        )
        department_summary=result.all()
        return department_summary

    async def get_above_average_salary(self,db:AsyncSession):
        department_total=(select(Department.name.label('name'),
                                 func.sum(Employee.salary).label("total_salary"))
                                .select_from(Department)
                                .join(Employee, Employee.department_id==Department.id)
                                .group_by(Department.id,Department.name).cte('department_total'))
        
        avg_salary_subquery=(select(func.avg(department_total.c.total_salary)).scalar_subquery())
        
        results=await db.execute(select(department_total.c.name,
                                        department_total.c.total_salary)
                                 .where(department_total.c.total_salary>avg_salary_subquery))

        return results.mappings().all()
    
department_repository=DepartmentRepository()