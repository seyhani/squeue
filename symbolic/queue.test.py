from symbolic.hist import SymbolicHistory
from symbolic.queue import SymbolicQueue
from symbolic.test_util import instantiate


def test_queue():
    h1 = SymbolicHistory.create("h1", [0, 0, 11, 12, 13, 14, 0, 0, 15, 0, 0])
    q1 = SymbolicQueue("q1", 3, h1)
    q1.set_deqs({7: 1})
    concrete_queue, queue_str = instantiate(q1)
    assert concrete_queue[5][2] == 13
    assert concrete_queue[8][0] == 12


def main():
    test_queue()


if __name__ == '__main__':
    main()
