# from sqlalchemy import select, func, case,desc
# async def get_top_traders(db):
#     total_value= func.sum(Trade.price*Trade.quantity).label("total_value")
    
#     result=await db.execute(select(
#         Trader.name.label("trader_name"),
#         total_value)
#         .select_from(Trader)
#         .join(Trade,Trade.trader_id==Trader.id)
#         .group_by(Trader.id,Trader.name)
#         .order_by(total_value.desc())
#         .limit(5)
#         )
    
"""
SELECT tr.name as trade_name, sum(t.price*t.quantity) as total_value
FROM Trader tr 
JOIN Trade t ON 
tr.id=t.trader_id
GROUP BY tr.id,tr.name
ORDER BY total_value DESC
LIMIT 5; 
"""

# avg_trade_value=(select(func.avg(Trade.price*Trade.quantity).label("avg_price")).scalar_subquery())

# results=await db.execute(select(Trade).where((Trade.price*Trade.quantity)>avg_trade_value))