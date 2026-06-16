from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Employee, Payroll
from app.schemas import PayrollCreate, PayrollStatus
from sqlalchemy import select,case, func

class PayrollRepository:
    async def create_payroll(self,db:AsyncSession,payroll_data:PayrollCreate,employee:Employee)->Payroll:
        payroll=Payroll(
                employee_id=payroll_data.employee_id,
                month=payroll_data.month,
                year=payroll_data.year,
                amount=employee.salary,
                status=PayrollStatus.PROCESSED
            )
        db.add(payroll)
        await db.flush()
        await db.refresh(payroll)
        return payroll
     
    async def get_for_update(self,db:AsyncSession,payroll_data:PayrollCreate)->Payroll:
        result=await db.execute(select(Payroll)
                                .filter(Payroll.employee_id==payroll_data.employee_id)
                                .filter(Payroll.month==payroll_data.month)
                                .filter(Payroll.year==payroll_data.year)
                                .with_for_update())
        
        return result.scalar_one_or_none()

    async def get_running_payroll_total(self,db:AsyncSession):
        result=await db.execute(select(
                                Payroll.id.label('payroll_id'),
                                Payroll.amount.label('amount'),
                                func.sum(Payroll.amount).over(order_by=Payroll.id).label('running_total')
        ))
        return result.all()
    
payroll_repository=PayrollRepository()