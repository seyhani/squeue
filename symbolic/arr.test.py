from symbolic.arr import IntArray
from symbolic.test_util import instantiate, assert_unsat


def test_creation():
    i1 = IntArray.create("i1", [0, 1, 2])
    concrete_array = instantiate(i1)
    assert concrete_array == [0, 1, 2]


def test_custom_constraint():
    i1 = IntArray.create("i1", [0, 1, 2])
    i1[1] = 3
    assert_unsat(i1)


def main():
    test_creation()
    test_custom_constraint()


if __name__ == '__main__':
    main()
