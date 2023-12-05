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
    rr1 = RoundRobinScheduler("rr1", T, qs, [ha1, ha2])
    s.add_struct(rr1)

    hb1 = single_id_hist("hb1", T, 1)
    hb2 = single_id_hist("hb2", T, 2)
    rr2 = RoundRobinScheduler("rr2", T, qs, [hb1, hb2])
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rr", T, qs, [rr1.out, rr2.out])
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
        forall(lambda t: (rr1.out | 1).cc(t) >= (rr1.out | 2).cc(t), range(1, T)),
        forall(lambda t: (rr2.out | 1).cc(t) >= (rr1.out | 2).cc(t), range(1, T)),
        (rr2.out | 2).cc() <= 0
    )

    q = exists(lambda t: (rro.out | 1).cc(t) - (rro.out | 2).cc(t) >= 4, range(1, T))

    s.add_constr(p, "P")
    s.add_constr(p1, "P1")
    # s.add_constr(p2, "P2")
    s.add_constr(Not(q), "~Q")
    # s.check_unsat()


def gap_example():
    T = 25
    pc = 8
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    h2 = single_id_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])
    rl = RateLimiter("rl", T, 2, rr.out)
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
        rr.out.project(1).maxg() == 1,
        rr.out.project(1).ming() == 1,
        rr.out.maxg() <= 0
    )

    q = And(
        exists(lambda t: abs_expr(out.project(1).cc(t) - out.project(2).cc(t)) >= 4, range(T)),
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
