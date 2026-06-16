from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.employee import employee_repository


class EmployeeService:
    async def get_top_5_employees(self, db: AsyncSession):
        top_employees = await employee_repository.get_top_5_employees(db)

        return top_employees

    async def get_employees_above_avg_salary(self, db: AsyncSession):
        employees = await employee_repository.get_employees_above_avg_salary(db)

        return employees

    async def get_employee_payrolls(self, db: AsyncSession, employee_id: int):
        results = await employee_repository.get_payrolls(db, employee_id)

        return [
            {
                "employee_id": employee.id,
                "payrolls": [
                    {
                        "id": payroll.id,
                        "amount": payroll.amount
                    }
                    for payroll in employee.payrolls
                ]
            }
            for employee in results
        ]


employee_service = EmployeeService()
