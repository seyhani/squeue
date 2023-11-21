from symbolic.arr import IntArray
from symbolic.smt_solver import SmtSolver
from symbolic.test_util import instantiate


def test_creation():
    s = SmtSolver()
    i1 = IntArray([0, 1, 2], name="i1", size=3)
    s.add_struct(i1)
    concrete_array = instantiate(i1)
    assert concrete_array == [0, 1, 2]


def test_custom_constraint():
    i1 = IntArray([0, 1, 2], name="i1", size=3)
    s = SmtSolver()
    s.add_struct(i1)
    s.add_constr(i1[1] == 3)
    s.check_unsat()


def main():
    test_creation()
    test_custom_constraint()


if __name__ == '__main__':
    main()
