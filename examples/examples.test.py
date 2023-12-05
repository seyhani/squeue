from z3 import And, Not

from symbolic.hist import single_id_hist
from schedulers.rl import RateLimiter
from schedulers.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import abs_expr
from symbolic.util import exists, forall


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
    s.check_unsat()


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

    s.check_unsat()


def main():
    cc_example()
    gap_example()


if __name__ == '__main__':
    main()
