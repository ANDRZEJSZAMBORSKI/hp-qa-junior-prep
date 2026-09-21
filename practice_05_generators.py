from collections.abc import Generator
def countdown(n: int):
    while n >= 1:
        yield n
        n -= 1

def squares(n: int):
    return (i ** 2 for i in range(n))

CASES = [
    {"id": "TC1", "tags": ["smoke", "auth"]},
    {"id": "TC2", "tags": ["regression"]},
    {"id": "TC3", "tags": ["smoke"]},
]

def iter_smoke(cases: list[dict]):
    for c in cases: 
        if "smoke" in c["tags"]:
            yield c

G1 = [
    {"id": "TC1", "tags": ["smoke"]},
    {"id": "TC2", "tags": ["regression"]},
]
G2 = [
    {"id": "TC3", "tags": ["smoke", "api"]},
]

def chain_smoke(*groups):
    for g in groups:
        yield from iter_smoke(g)

def take(n, it):
    it = iter(it)
    for _ in range(n):
        try:
            yield next(it)
        except StopIteration:
            return

def main():
    assert list(countdown(3)) == [3, 2, 1]
    assert list(countdown(0)) == []
    assert list(countdown(1)) == [1]
    g = countdown(2)
    assert list(g) == [2, 1]
    assert list(g) == []
    print('countdown OK')

    assert list(squares(4)) == [0, 1, 4, 9]
    g = squares(3)
    assert hasattr(g, '__next__')
    assert type(g) == type((x for x in range(1)))
    assert isinstance(g, Generator)
    assert sum(squares(5)) == 30
    print('squares OK')

    assert list(c["id"] for c in iter_smoke(CASES)) == ["TC1", "TC3"]
    print('iter_smoke OK')

    assert list(c["id"] for c in chain_smoke(G1, G2)) == ["TC1", "TC3"]
    assert list(chain_smoke()) == []
    print('chain_smoke OK')

    assert list(take(2, iter_smoke(CASES))) == [
        {"id": "TC1", "tags": ["smoke", "auth"]},
        {"id": "TC3", "tags": ["smoke"]},
    ]
    assert list(take(0, countdown(5))) == []
    assert list(take(10, countdown(3))) == [3, 2, 1]
    assert list(take(1, countdown(5))) == [5]
    assert list(take(2, countdown(5))) == [5, 4]
    print('take OK')

if __name__ == '__main__':
    main()


