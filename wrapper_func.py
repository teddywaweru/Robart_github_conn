from time import time

def measure_time(func):
    def wrapper(*args,**kwargs):
        from time import time
        start = time()
        result = func(*args,**kwargs)
        print(f'Time to run{str(func)}: {time() - start}')
        return result
    return wrapper

