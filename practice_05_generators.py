from collections.abc import Generator
def countdown(n: int):
    while n >= 1:
        yield n
        n -= 1

def squares(n: int):
    return (i ** 2 for i in range(n))

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

if __name__ == '__main__':
    main()


