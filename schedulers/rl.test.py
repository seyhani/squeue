from schedulers.rl import RateLimiter
from symbolic.hist import non_trivial_hist, create_hist
from symbolic.smt_solver import SmtSolver


def test_rl():
    T = 8
    h = create_hist("h1", [0, 1, 1, 1, 1, 0, 0, 1], T)
    rl = RateLimiter("rl", T, 3, h)
    s = SmtSolver()
    s.add_struct(rl)
    m = s.check_sat()
    assert m.eval(rl.out.maxg()) == m.eval(rl.out.ming()) == 1
    assert m.eval(rl.out.cc()) == 3


def main():
    test_rl()


if __name__ == '__main__':
    main()
