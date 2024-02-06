from math import floor, ceil

from z3 import And, Not

from schedulers.rr import RoundRobinScheduler
from symbolic.hist import single_id_hist, create_hist, SymbolicHistory, multiple_id_hist
from symbolic.smt_solver import SmtSolver
from symbolic.squeue import SymbolicQueue
from symbolic.util import exists, abs_expr, forall


def simple():
    T = 5
    h1 = single_id_hist("h1", T, 1)
    p = h1.cc() > 2
    s = SmtSolver()
    s.add_struct(h1)
    s.add_constr(p)
    s.add_constr(Not(p))
    m = s.check_sat()
    print("H1: ", h1.eval(m))


def full_half():
    T = 20
    maxc1 = T - 1
    maxc2 = maxc1 - 1
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    # h1 = create_hist("h1", [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1], T)
    # h1 = create_hist("h1", [0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0], T)
    h2 = multiple_id_hist("h2", T, [1, 2])
    # h2 = create_hist("h2", [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], T)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])

    head_mark = 3
    tail_mark = T - 5

    head = range(0, head_mark)
    middle = range(head_mark, tail_mark)
    offset = 4
    middle1 = range(head_mark + offset, tail_mark)
    tail = range(tail_mark, T)
    print([i for i in head])
    print([i for i in middle])
    print([i for i in middle1])
    print([i for i in tail])

    def envelope(h: SymbolicHistory, envl, tau: int, rng: range):
        return forall(lambda t: h.cc(t) - h.cc(t - tau) >= envl(tau), rng)

    always_backlogged = lambda tau: floor(tau / 2)

    p1 = And(
        envelope(h1, always_backlogged, 4, middle)
    )

    p2 = And(
        (h2 | 2).cc() >= 9,
    )

    p3 = And(
        envelope(h2 | 1, always_backlogged, 4, middle)
    )

    q = And(
        envelope(rr.out | 1, lambda tau: (3 * tau) / 4, 4, middle1)
    )

    # p2 = And(
    #     h1.cc() <= ceil(maxc1 / 2)
    # )

    # q = And(
    #     (rr.out | 1).cc() >= maxc2 / 2
    # )

    s.add_struct(rr)

    s.add_constr(p1, "p1")
    s.add_constr(p2, "p2")
    s.add_constr(p3, "p3")
    # s.add_constr(q, "q")
    s.add_constr(Not(q), "q")
    m = s.check_sat()
    print("H1: ", h1.eval(m))
    print("H2: ", h2.eval(m))
    print("rr: ", rr.out.eval(m))


def initial_state():
    T = 16
    maxc1 = T - 1
    s = SmtSolver()
    # h1 = create_hist("h1", [11, 12, 13, 14, 15, 16], T)
    # h2 = create_hist("h2", [21, 22, 23, 24, 25, 26], T)
    h1 = single_id_hist("h1", 10, 1)
    q = SymbolicQueue("1", 3, h1)
    p = And(
        h1.cc(5) == 5,
        q.cdeq(5) <= 0
    )
    s.add_struct(q)
    s.add_constr(p, "p")
    m = s.check_sat()
    print(q.eval_to_str(m))
    return
    # h2 = single_id_hist("h2", T, 2)
    # rr = RoundRobinScheduler("rr", T, 2, [h1, h2])
    # out = rr.out
    # p1 = And(
    #     h1.cc(6) == 6
    # )
    # p2 = And(
    #     h2.cc(6) == 6
    # )
    # q = And(
    #     out.cc() <= 9
    # )
    # s.add_struct(rr)
    # s.add_constr(p1, "p1")
    # s.add_constr(p2, "p2")
    # s.add_struct(rr)
    # s.add_constr(q, "q")
    # m = s.check_sat()
    # print("h1: ", h1.eval(m))
    # print("h2: ", h2.eval(m))
    # print("out: ", rr.out.eval(m))
    # return


def main():
    # simple()
    full_half()
    # initial_state()


if __name__ == '__main__':
    main()
