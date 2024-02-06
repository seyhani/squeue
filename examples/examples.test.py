from math import floor

from z3 import And, Not, Xor

from schedulers.rl import RateLimiter
from schedulers.rr import RoundRobinScheduler
from symbolic.hist import single_id_hist, SymbolicHistory
from symbolic.smt_solver import SmtSolver
from symbolic.util import abs_expr
from symbolic.util import exists, forall
from utils.logger import Logger


def cc_example():
    T = 12
    qs = 5
    s = SmtSolver()

    ha1 = single_id_hist("ha1", T, 1)
    ha2 = single_id_hist("ha2", T, 2)
    rra = RoundRobinScheduler("rra", T, qs, [ha1, ha2])
    ha = rra.out
    s.add_struct(rra)

    hb1 = single_id_hist("hb1", T, 1)
    hb2 = single_id_hist("hb2", T, 2)
    rrb = RoundRobinScheduler("rrb", T, qs, [hb1, hb2])
    hb = rrb.out
    s.add_struct(rrb)

    rro = RoundRobinScheduler("rr", T, qs, [rra.out, rrb.out])
    ho = rro.out
    s.add_struct(rro)

    p = And(
        forall(lambda t: ha1.cc(t) + hb1.cc(t) >= t, range(1, T)),
        forall(lambda t: ha2.cc(t) + hb2.cc(t) >= t, range(1, T))
    )

    p1 = And(
        forall(lambda t: (ha1 | 1).cc(t) >= (ha2 | 2).cc(t), range(1, T)),
        forall(lambda t: (hb1 | 1).cc(t) >= (ha2 | 2).cc(t), range(1, T)),
        (hb2 | 2).cc() <= 0
    )

    p2 = And(
        forall(lambda t: (ha | 1).cc(t) >= (ha | 2).cc(t), range(1, T)),
        forall(lambda t: (hb | 1).cc(t) >= (ha | 2).cc(t), range(1, T)),
        (hb | 2).cc() <= 0
    )

    q = exists(lambda t: (ho | 1).cc(t) - (ho | 2).cc(t) >= 4, range(1, T))

    s.add_constr(p, "P")
    s.add_constr(p1, "P1")
    # s.add_constr(p2, "P2")
    s.add_constr(Not(q), "~Q")
    Logger.loading("Checking unsat", s.check_unsat)


def gap_example():
    T = 25
    pc = 8
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    h2 = single_id_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])
    hrr = rr.out
    rl = RateLimiter("rl", T, 2, rr.out)
    hrl = rl.out
    out = rl.out

    p = And(
        h1.maxg() <= 2,
        h1.cc(1) >= 1,
        h1.cc() >= pc,
        h2.maxg() <= 2,
        h2.cc(1) >= 1,
        h2.cc() >= pc,
    )

    p1 = And(
        h1.maxg() <= 1,
        h2.maxg() <= 1
    )

    p2 = And(
        hrr.project(1).maxg() == 1,
        hrr.project(1).ming() == 1,
        hrr.maxg() <= 0
    )

    q = And(
        exists(lambda t: abs_expr((hrl | 1).cc(t) - (hrl | 2).cc(t)) >= 4, range(T)),
    )

    s.add_struct(rr)
    s.add_struct(rl)

    s.add_constr(p, "P")
    s.add_constr(p1, "P1")
    # s.add_constr(p2, "P2")
    s.add_constr(Not(q), "~Q")
    Logger.loading("Checking unsat", s.check_unsat)


def rr_example():
    T = 15
    maxc1 = T - 1
    maxc2 = T - 2
    maxc3 = T - 3
    qs = 5
    s = SmtSolver()

    ha1 = single_id_hist("ha1", T, 1)
    ha2 = single_id_hist("ha2", T, 2)
    rra = RoundRobinScheduler("rra", T, qs, [ha1, ha2])
    ha = rra.out
    s.add_struct(rra)

    hb1 = single_id_hist("hb1", T, 1)
    hb2 = single_id_hist("hb2", T, 2)
    rrb = RoundRobinScheduler("rrb", T, qs, [hb1, hb2])
    hb = rrb.out
    s.add_struct(rrb)

    rro = RoundRobinScheduler("rr", T, qs, [rra.out, rrb.out])
    ho = rro.out
    s.add_struct(rro)

    p = And(
        ha2.cc() >= maxc1,
        ha1.cc() + hb1.cc() <= maxc1
    )

    def envelope(h: SymbolicHistory, envl, tau: int, rng: range):
        return forall(lambda t: h.cc(t) - h.cc(t - tau) >= envl(tau), rng)

    head_mark = 2
    tail_mark = T - 3
    head = range(0, head_mark)
    middle = range(head_mark, tail_mark)
    offset = 5
    middle1 = range(head_mark + offset, tail_mark)
    tail = range(tail_mark, T)

    p1 = And(
        hb2.cc() == 0,
        envelope(ha1, lambda tau: tau / 2, 4, middle),
        envelope(hb1, lambda tau: tau / 2, 4, middle),
        # envelope(ha1, 2),
        # forall(lambda t: ha1.cc(t) >= floor(t / 2), range(2, T)),
        # forall(lambda t: hb1.cc(t) >= floor(t / 2), range(2, T))
    )

    p2 = And(
        (hb | 2).cc() == 0,
        envelope(ha | 1, lambda tau: tau / 2, 2, middle),
        envelope(hb, lambda tau: tau / 2, 2, middle),
        # forall(lambda t: (ha | 1).cc(t) >= floor(t / 2), range(2, T)),
        # forall(lambda t: hb.cc(t) >= floor(t / 2), range(2, T))
    )

    # p1 = And(
    #     ha1.cc() + hb1.cc() <= maxc1
    # )
    #
    # pa1 = And(
    #     forall(lambda t: ha1.cc(t) >= t / 2, range(1, T, 4))
    # )
    #
    # pb1 = And(
    #     forall(lambda t: hb1.cc(t) >= t / 2, range(1, T, 4))
    # )
    #
    # pa2 = And(
    #     ha2.cc() >= maxc1
    # )
    #
    # pb2 = And(
    #     hb2.cc() <= 0
    # )

    q = And(
        envelope(ho | 1, lambda tau: (3 * tau) / 4, 4, middle1)
    )

    s.add_constr(p, "p")
    s.add_constr(p1, "p1")
    # s.add_constr(p2, "p2")
    # s.add_constr(pa1, "pa1")
    # s.add_constr(pb1, "pb1")
    # s.add_constr(pa2, "pa2")
    # s.add_constr(pb2, "pb2")
    # s.add_constr(q, "q")
    s.add_constr(Not(q), "q")
    m = s.check_sat()

    print("ha1: ", ha1.eval(m))
    print("ha2: ", ha2.eval(m))
    print("hb1: ", hb1.eval(m))
    print("hb2: ", hb2.eval(m))
    print("ha : ", ha.eval(m))
    print("hb : ", hb.eval(m))
    print("ho : ", ho.eval(m))


def main():
    # cc_example()
    # gap_example()
    rr_example()


if __name__ == '__main__':
    main()
