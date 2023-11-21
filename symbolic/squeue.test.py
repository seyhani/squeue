from symbolic.base import LabeledExpr
from symbolic.hist import create_hist
from symbolic.squeue import SymbolicQueue
from symbolic.test_util import instantiate


def test_queue():
    h1 = create_hist("h1", [0, 0, 11, 12, 13, 14, 0, 0, 15, 0, 0])
    q1 = SymbolicQueue("q1", 3, h1)
    concrete_queue = instantiate(q1, [
        LabeledExpr(q1.head_pkt(5) == 12, "head(5) == 12"),
        LabeledExpr(q1.head_pkt(6) == 13, "head(6) == 13")
    ])
    assert concrete_queue[5][0] == 12
    assert concrete_queue[6][0] == 13


def main():
    test_queue()


if __name__ == '__main__':
    main()
