from functools import wraps
import time
from functools import update_wrapper

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

def logged_broken(fn):
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        return res
    return wrapper

def logged_ok(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        return res
    return wrapper

@logged_broken
def alpha():
    """Alpha doc."""
    return 1

@logged_ok
def beta():
    """Beta doc."""
    return 2

def ensure_non_negative(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        return 0 if res < 0 else res
    return wrapper

@ensure_non_negative
def score(x):
    """Score fn."""
    return x

def retry(times: int = 3, exc_types=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except exc_types as e:
                    print(f"Attempt: {i + 1}")
                    last = e
            raise last
        return wrapper
    return  decorator

calls = {"n": 0}
@retry(times=3, exc_types=(ValueError,))
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise ValueError("fail")
    return "ok"

@retry(times=2, exc_types=(ValueError,))
def always_fail():
    raise ValueError("nope")

# pipeline = logged(timed(pipeline))
@logged # Outer decorator
@timed # Inner decorator
def pipeline(x):
    """Pipeline fn."""
    time.sleep(0.01)
    return x * 2

def count_calls(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        print(f"calls: {wrapper.calls}")
        return fn(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

class Counter:
    def __init__(self):
        self.value = 0

    @count_calls
    def inc(self):
        """Increment."""
        self.value += 1
        return self.value

def once(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not wrapper.called:
            wrapper.result = fn(*args, **kwargs)
            wrapper.called = True
        return wrapper.result
    wrapper.called = False
    wrapper.result = None
    return wrapper

@once
def init_config():
    """Init once."""
    print("init")
    return {"ok": True}

def memoize(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in wrapper.cache:
            return wrapper.cache[key]
        wrapper.cache[key] = fn(*args, **kwargs)
        wrapper.calls += 1
        return wrapper.cache[key]
    wrapper.cache: dict = {}
    wrapper.calls = 0
    return wrapper

@memoize
def add_slow(a, b):
    print("Function is running")
    return a + b

@memoize
def fib(n):
    print(f"Calculating fib({n})")

    if n <= 1:
        return n

    return fib(n - 1) + fib(n - 2)    

class CallCounter:
    def __init__(self, fn):
        self._fn = fn
        self._calls = 0
        update_wrapper(self, fn)

    @property
    def fn(self):
        return self._fn

    @property
    def calls(self):
        return self._calls

    def __call__(self, *args, **kwds):
        self._calls += 1
        return self.fn(*args, **kwds)

@CallCounter
def greet(name):
    """Say hello."""
    return f"Hello, {name}"


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

    assert alpha.__name__ == "wrapper"
    assert alpha.__doc__ != "Alpha doc."   # обычно None
    assert beta.__name__ == "beta"
    assert beta.__doc__ == "Beta doc."
    assert alpha() == 1 and beta() == 2
    print("wraps OK")

    assert score(-5) == 0
    assert score(7) == 7
    assert score(0) == 0
    assert score.__name__ == "score"
    print("ensure_non_negative OK")

    assert flaky() == "ok"
    assert calls["n"] == 3

    try:
        always_fail()
        assert False
    except ValueError as e:
        assert "nope" in str(e)
    print("retry OK")
        
    assert pipeline(5) == 10
    assert pipeline.__name__ == "pipeline"
    assert pipeline.__doc__ == "Pipeline fn."
    print("stacked OK")

    c = Counter()
    assert c.inc() == 1
    assert c.inc() == 2
    assert c.inc.__name__ == "inc"
    assert c.inc.__doc__ == "Increment."
    assert c.inc.calls == 2
    print("method decorator OK")

    a = init_config()
    b = init_config()
    assert a is b
    assert a == {"ok": True}
    assert init_config.__name__ == "init_config"
    print("once OK")

    a = add_slow(2, 3)
    b = add_slow(2, 3)
    assert a == 5
    assert b == 5
    assert add_slow.calls == 1

    a = fib(5)
    assert a == 5
    assert fib.calls == 6
    print("memoize OK")

    for _ in range(10):
        a = greet('Artur')
    assert a == "Hello, Artur"
    assert greet.__name__ == 'greet'
    assert greet.__doc__ == 'Say hello.'
    assert greet.calls == 10
    assert greet(name="Artur") == "Hello, Artur"
    assert greet.calls == 11
    print('class CallCounter OK')

if __name__ == "__main__":
    main()


