# N+1 queries problem means that one query then N more queries 
# the better solution would be to use joinedload(trader.trades)
# this reduces the queries to one single query performs a left join  and combines the two tables
# then another option is to use selectinload can be used when the relationship is very complex
# this performs 2 queries 
from sqlalchemy import Column,Integer,String,Float,func,select,count,sum,case,ForeignKey
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.orm import relationship

class User():
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)

    orders=relationship('Order',back_populates='user')
    
class Order():
    __tablename__='orders'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey('users.id'),nullable=False)
    total_amount=Column(Float,nullable=False)

    user=relationship('User',back_populates='orders')
    items=relationship('OrderItem',back_populates='order')
    

class OrderItem():
    __tablename__='orderitems'
    
    id=Column(Integer,primary_key=True,index=True)
    order_id=Column(Integer,ForeignKey('orders.id'),nullable=False)
    product_name=Column(String,nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    
    order=relationship('Order',back_populates='orderitems')
    
    

async def get_user_orders(user_id,db):
    results=await db.execute(select(User.name).where(User.id==user_id))
    user_data=results.scalar_one_or_none()

    results=await db.execute(select(Order).options(selectinload(Order.items)).where(Order.user_id==user_id))
    orders=results.scalars().all()
    

    return {
        "user":user_data,
        "orders":[
            {
                "order_id": order.id,
                "total_amount":order.total_amount,
                "items":[
                    {
                        "id":item.id,
                        "quantity":item.quantity
                    }
                    for item in order.items
                ]
            }
            for order in orders
        ]
    }
    
async def get_top_users(db):
    total_order_amount=func.sum(Order.total_amount).label('total_order_value')
    result=await db.execute(select(
                        User.name.label('name'),
                        total_order_amount)
                        .select_from(User)
                        .join(Order,Order.user_id==User.id)
                        .group_by(User.name,User.id)
                        .order_by(total_order_amount.desc())
                        .limit(5)
                        )
    top_users=result.mappings().all()
    
    return top_users

# use scalar when either only one column is being selected or an entire object is being selected a list of objects

async def get_users_above_average_spend(db):
    user_spends= (select(
                        Order.user_id,
                        func.sum(Order.total_amount).label('total_spent'))
                        .group_by(Order.user_id)
                        .cte('user_spends')
                        )
    
    average_spending=(select(func.avg(user_spends.c.total_spent)).scalar_subquery())
    
    result=await db.execute(select(user_spends.c.user_id,
                                User.name,
                                user_spends.c.total_spent)
                                .select_from(user_spends)
                                .join(User,user_spends.c.user_id==User.id)
                                .where(user_spends.c.total_spent>average_spending)
                                )
    rows=result.all()
    return rows

async def get_running_sales(db):
    query=select(Order.id,
                 Order.total_amount,
                 func.sum(Order.total_amount)
                 .over(order_by=Order.id)
                 .label('running_total')
                 )
    results=await db.execute(query)
    return results.all()

async def create_order(db,user_id,items):
    async with db.begin():
        result=await db.execute(select(User).where(User.id==user_id))
        user=result.scalar_one_or_none()
        if not user:
            return None # raise HTTP error
        
        total_amount=0
        for item in items:
            total_amount+=item.price*item.quantity
        
        order=Order(
            user_id=user_id,
            total_amount=total_amount
        )
        db.add(order)
        await db.flush()
        for item in items:
            order_item=OrderItem(
                order_id=order.id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.price
            )
            db.add(order_item)
        await db.flush()
        
        