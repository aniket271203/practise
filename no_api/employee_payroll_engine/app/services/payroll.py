from app.schemas import PayrollCreate, PayrollStatus
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.employee import employee_repository
from app.repositories.payroll import payroll_repository
from app.models import Payroll


class PayrollService:
    async def process_payroll(self, db: AsyncSession, payroll_data: PayrollCreate) -> Payroll:
        # validatae the employee exists
        # check if payroll exists so no duplicate check with same employee month and year
        # create a payroll if not exists
        # amount=employee.salary, status=processed
        async with db.begin():
            employee = await employee_repository.get_for_update(db, payroll_data.employee_id)

            if not employee:
                return None  # raise error employee does not exist

            payroll = await payroll_repository.get_for_update(db, payroll_data)

            if payroll:
                return None  # raise error already processed payroll
            try:
                payroll = await payroll_repository.create_payroll(db, payroll_data, employee)
                return payroll
            except Exception as e:
                raise e

    async def get_running_payroll_total(self, db: AsyncSession):
        payroll_results = await payroll_repository.get_running_payroll_total(db)

        return [
            {
                "payroll_id": payroll.payroll_id,
                "amount": payroll.amount,
                "running_total": payroll.running_total
            }
            for payroll in payroll_results
        ]


payroll_service = PayrollService()


"""
TASK 8 
db.commit should not exist in the repositories because this entire operation is suppsoed to be atomic which means either all operatiosn run or none do 
and that is why we create a trasaction boundary and use flush which creates a temporary update the to database which is made permanent only after the trabsaction completes and in case any exception is raiased in between the tranasaction automatically rollsback so that the database is back to its original state
useing with db.begin()
"""
