from dataclasses import dataclass
from enum import Enum

@dataclass
class WarehouseCreate:
    name:str
    location:str

@dataclass
class ProductCreate:
    name:str
    price:float


@dataclass
class InventoryCreate:
    warehouse_id:int
    product_id:int
    quantity:int

class ShipmentStatus(str,Enum):
    RESERVED='reserved'
    SHIPPED='shipped'
    CANCELLED='cancelled'

@dataclass
class ShipmentCreate:
    warehouse_id:int
    product_id:int
    quantity:int
    

   