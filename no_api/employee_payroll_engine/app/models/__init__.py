from sqlalchemy import Column, Integer,String,Float,DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__="departments"
    
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String,nullable=False)
    
    employees=relationship('Employee', back_populates='department')
    
    def __repr__(self):
        return f"Department( id={self.id} name={self.name})"



class Employee(Base):
    __tablename__='employees'
    
    id=Column(Integer,primary_key=True, index=True)
    name=Column(String,nullable=False)
    department_id=Column(Integer,ForeignKey('departments.id'),nullable=False)
    salary=Column(Float,nullable=False) 
    
    department=relationship("Department",back_populates='employees')
    payrolls=relationship('Payroll',back_populates='employee')
    
    def __repr__(self):
        return f"Employee(id={self.id} department_id={self.department_id})"

class Payroll(Base):
    __tablename__='payrolls'
    __table_args__ = (
            UniqueConstraint(
                "employee_id",
                "month",
                "year"
            ),
        )
    
    id=Column(Integer,primary_key=True,index=True)
    employee_id=Column(Integer,ForeignKey('employees.id'),nullable=False)
    month=Column(String,nullable=False)
    year=Column(Integer,nullable=False)
    amount=Column(Float,nullable=False)
    status=Column(String,nullable=False)
    
    employee=relationship("Employee",back_populates='payrolls')
    
    def __repr__(self):
        return f"Payroll(id={self.id} empl_id={self.employee_id} status={self.status})"