from schedulers.rr import RoundRobinScheduler
from symbolic.hist import create_hist
from symbolic.test_util import instantiate


def test_rr():
    h0 = create_hist("h0", [10, 0, 0, 20, 0, 0])
    h1 = create_hist("h1", [0, 0, 0, 11, 0, 0])
    h2 = create_hist("h2", [0, 0, 12, 22, 0, 0])
    rr = RoundRobinScheduler("rr", 10, 3, [h0, h1, h2])
    c = instantiate(rr)
    assert c[2] == 10
    assert c[4] == 12
    assert c[5] == 20
    assert c[6] == 11


def main():
    test_rr()


if __name__ == '__main__':
    main()
