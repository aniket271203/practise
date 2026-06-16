from enum import Enum

class PayrollStatus(str,Enum):
    PENDING="pending"
    PROCESSED="processed"

class PayrollCreate:
    employee_id:int
    month:str
    year:int
    
class EmployeeCreate:
    name:str
    department_id:int
    salary:float
    
class DepartmentCreate:
    name:str