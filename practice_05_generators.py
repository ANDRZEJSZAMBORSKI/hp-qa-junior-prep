def countdown(n: int):
    while n >= 1:
        yield n
        n -= 1

def main():
    assert list(countdown(3)) == [3, 2, 1]
    assert list(countdown(0)) == []
    assert list(countdown(1)) == [1]
    g = countdown(2)
    assert list(g) == [2, 1]
    assert list(g) == []
    print('countdown OK')

if __name__ == '__main__':
    main()


