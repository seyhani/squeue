from z3 import And, Not

from symbolic.hist import non_trivial_hist
from schedulers.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import max_expr


def test():
    T = 15
    s = SmtSolver()
    h1 = non_trivial_hist("h1", T, 1)
    h2 = non_trivial_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])

    rr.run()

    s.add_struct(rr)

    # m1 = Int("m1")
    # m2 = Int("m2")
    p = And(
        # h1.maxg() >= 0,
        # h2.maxg() >=
    )
    # s.add_constr(m1 >= 0)
    # s.add_constr(m2 >= 0)

    q = And(
        rr.out.maxg() <= max_expr(h1.maxg(), h2.maxg())
    )

    s.add_constr(p)
    # s.add_constr(q)
    s.add_constr(Not(q))

    m = s.check_sat()
    print(m.eval(rr.out.maxg()))
    print(m.eval(max_expr(h1.maxg(), h2.maxg())))
    print(m.eval(q))
    print("h1: ", h1.eval(m))
    print("h2: ", h2.eval(m))
    print("rr: ", rr.eval(m))
    # print("h1: ", [m.eval(h1.cc(t)) for t in range(T)])
    # print("h2: ", [m.eval(h2.cc(t)) for t in range(T)])
    # print("rr: ", [m.eval(rr.out.cc(t)) for t in range(T)])


def main():
    test()


if __name__ == '__main__':
    main()
