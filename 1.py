import time
def my_deco(func):
    def wrapper(*args,**kwargs):
        start_time=time.perf_counter()
        val=func(*args,**kwargs)
        end_time=time.perf_counter()
        print(end_time-start_time)
        return val
    return wrapper

@my_deco
def sum_number(a,b):
    return a+b


with open():
    enter exit