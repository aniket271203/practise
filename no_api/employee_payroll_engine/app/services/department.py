from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.department import department_repository


class DepartmentService:
    async def get_department_summary(self, db: AsyncSession):
        department_summary = await department_repository.get_department_summary(db)

        return [
            {
                "department": department.department,
                "employees": department.employee_count,
                "total_salary": department.total_salary
            }
            for department in department_summary
        ]
        
    async def get_departments_above_average_salary(self,db:AsyncSession):
        result=await department_repository.get_above_average_salary(db)
        
        return result
department_service=DepartmentService()