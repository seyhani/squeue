from symbolic.arr import IntArray
from symbolic.hist import non_trivial_hist
from symbolic.smt_solver import SmtSolver
from symbolic.test_util import instantiate


def test_non_trivial_hist():
    h = non_trivial_hist("h", 4, 7)
    ch = instantiate(h)
    assert ch[0] == 0
    assert ch[1] == 7
    assert ch[2] == 7 or ch[3] == 7


def main():
    test_non_trivial_hist()


if __name__ == '__main__':
    main()
