from functools import wraps
import time

def timed(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("Function name: ", fn.__name__)
        start = time.time()
        res = fn(*args, **kwargs)
        print(f"Time: {time.time() - start}")
        return res
    return wrapper

@timed
def slow_add(a: int, b: int) -> int:
    """Add two numbers."""
    time.sleep(0.05)
    return a + b

def logged(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"Function name: {fn.__name__}")
        print(f"Function arguments: args={args}, kwargs={kwargs}")
        res = fn(*args, **kwargs)
        print(f"Function result: {res}")
        return res
    return wrapper

@logged
def calc(a, b=0):
    """Calc sum."""
    return a + b


def main():
    res = slow_add(5, 5)
    assert res == 10
    assert slow_add(2, 3) == 5
    assert slow_add(-2, 5) == 3
    assert slow_add(0, 0) == 0
    assert slow_add.__name__ == "slow_add"
    assert slow_add.__doc__ == "Add two numbers."
    assert slow_add(10, b=20) == 30
    assert slow_add(a=10, b=20) == 30
    assert slow_add(10, 20) == 30
    assert isinstance(res, int)
    print("timed OK")

    assert calc(2, 3) == 5
    assert calc(2, b=3) == 5
    assert calc.__name__ == "calc"
    assert calc.__doc__ == "Calc sum."
    print("logged OK")

if __name__ == "__main__":
    main()


