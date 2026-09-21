import time
from contextlib import contextmanager
import tempfile
import os
from pathlib import Path

class StepTimer:
    def __init__(self, name: str):
        self._name = str(name)
        self._time_prev = None
        self._finish = None

    @property
    def name(self):
        return self._name

    @property
    def time_prev(self):
        return self._time_prev

    @time_prev.setter
    def time_prev(self, data):
        if isinstance(data, float) and data >=0:
           self._time_prev = data
        else:
            raise ValueError(f"Invalid data: {data}")

    @property
    def time_elapsed(self):
        return time.perf_counter() - self.time_prev

    @property
    def finish(self):
        return self._finish

    @finish.setter
    def finish(self, data):
        if isinstance(data, float) and data >=0:
            self._finish = data
        else:
            raise ValueError(f"Invalid data: {data}")
        
    def __enter__(self):
        self.time_prev = time.perf_counter()
        print(f"[START] {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.finish = self.time_elapsed
        status = "FAIL" if exc_type else "OK"
        print(f"[END] {self.name} {status} in {self.finish:.3f}s")
        return False 

@contextmanager
def step_timer(name: str):    
    print(f"[START] {name}")
    start = time.perf_counter()
    try:
        yield name
    finally:
        finish = time.perf_counter() - start
        print(f"[END] {name} in {finish:.3f}s")

@contextmanager
def temp_text_file(text: str):
    f = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False)
    f.write(text)
    f.flush()
    f.close()

    try:
        yield f.name
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)

def main():
    with StepTimer("ok-step") as t:
        time.sleep(0.01)
    assert t.finish >= 0.01
    try:
        with StepTimer("fail-step") as t2:
            raise ValueError("boom")
    except ValueError:
            pass
    assert t2.finish >= 0
    print('class StepTimer OK')

    with step_timer("cm2-ok"):
        time.sleep(0.01)
    try:
        with step_timer("cm2-fail"):
            raise RuntimeError("x")
    except RuntimeError:
        pass
    print('step_timer OK')

    with temp_text_file("hello qa") as path:
        assert Path(path).exists()
        assert Path(path).read_text(encoding="utf-8") == "hello qa"
    assert not Path(path).exists()
    try:
        with temp_text_file("x") as path2:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert not Path(path2).exists()
    print("temp_text_file OK")

if __name__ == '__main__':
    main()

        