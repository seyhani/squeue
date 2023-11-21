from symbolic.base import LabeledExpr
from symbolic.hist import create_hist
from symbolic.squeue import SymbolicQueue
from symbolic.test_util import instantiate


def test_queue():
    h = create_hist("h", [0, 0, 11, 12, 13, 14, 0, 0, 15, 0, 0])
    q = SymbolicQueue("q", 3, h)
    constrs = [
        LabeledExpr(q.head_pkt(5) == 12, "head(5) == 12"),
        LabeledExpr(q.head_pkt(6) == 13, "head(6) == 13")
    ]
    concrete_queue = instantiate(q, constrs)
    assert concrete_queue[5][0] == 12
    assert concrete_queue[6][0] == 13


def test_dequeue():
    h = create_hist("h", [0, 11, 12, 13, 14, 0, 0, 15, 0, 0])
    q = SymbolicQueue("q", 3, h)
    q.set_dequeues({6: 1, 7: 1, 8: 1})
    concrete_queue = instantiate(q)
    assert concrete_queue[9][0] == 15


def main():
    test_queue()
    test_dequeue()


if __name__ == '__main__':
    main()
