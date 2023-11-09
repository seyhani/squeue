from random import random

from z3 import Solver, Or, IntVal, If, And, Xor, Int

from symbolic.hist import SymbolicHistory
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver


def t():
    s = Solver()
    s.set(unsat_core=True)
    s.set('smt.arith.random_initial_value', True)
    s.set('random_seed', 200)
    h1 = SymbolicHistory("h1", 10)
    h2 = SymbolicHistory("h2", 10)
    rr = RoundRobinScheduler("rr1", 3, [h1, h2])
    rr.run()

    for t in range(1, 10):
        s.assert_and_track(h1[t] <= 2, "h1[{}] <= 2".format(t))
        s.assert_and_track(h2[t] <= 2, "h2[{}] <= 2".format(t))
    s.assert_and_track(And(
        ccount(rr.out, 1, 9) - ccount(rr.out, 2, 9) >= 4,
    ), "query")
    add_constrs(s, rr)

    print(s.check())
    m = s.model()
    print(rr.eval(m))


# h00 h01        h10 h11
#   rr0            rr1
#   out0            out1
#           rr
#           out

def ccount(hist: SymbolicHistory, id: int, t: int):
    res = IntVal(0)
    for i in range(1, t):
        res += If(hist[i] == id, 1, 0)
    return res


def test():
    h11 = SymbolicHistory("h11", 10)
    print(h11.constrs())
    s = SmtSolver()
    s.add_constrs(h11)
    s.add_constr(h11[1] == 2, "bar")
    s.add_constr(h11[1] == 3, "baz")
    # s.add_constr(h11[1] == 2)
    # s.add_constr(h11[1] == 3)
    # m = s.check_sat()
    # print(h11.eval(m))
    core = s.check_unsat()
    print(core)
    return
    T = 12
    qs = 3
    s = Solver()
    s.set('smt.arith.random_initial_value', True)
    s.set('random_seed', 300)
    s.set(unsat_core=True)

    h11 = SymbolicHistory("h11", T)
    h12 = SymbolicHistory("h12", T)
    rr1 = RoundRobinScheduler("rr1", T, qs, [h11, h12])
    rr1.run()
    add_constrs(s, rr1)

    h21 = SymbolicHistory("h21", T)
    h22 = SymbolicHistory("h22", T)
    rr2 = RoundRobinScheduler("rr2", T, qs, [h21, h22])
    rr2.run()
    add_constrs(s, rr2)

    rr = RoundRobinScheduler("rr", T, qs, [rr1.out, rr2.out])
    rr.run()
    add_constrs(s, rr)

    for t in range(1, T):
        s.assert_and_track(Or(h11[t] == 0, h11[t] == 1), "h11[{}] = 0 | 1".format(t))
        s.assert_and_track(Or(h21[t] == 0, h21[t] == 1), "h21[{}] = 0 | 1".format(t))
        s.assert_and_track(Or(h12[t] == 0, h12[t] == 2), "h12[{}] = 0 | 2".format(t))
        s.assert_and_track(Or(h22[t] == 0, h22[t] == 2), "h22[{}] = 0 | 2".format(t))
        s.assert_and_track(Xor(h11[t] > 0, h21[t] > 0), "enq[{}](h11,h21) == 1".format(t))
        s.assert_and_track(Xor(h12[t] > 0, h22[t] > 0), "enq[{}](h12,h22) == 1".format(t))
    #
    s.assert_and_track(Or([And(rr.out[t] == 1, rr.out[t - 1] == 1, rr.out[t - 2] == 1) for t in range(2, T)]),
                       "starvation")

    print(s.check())
    m = s.model()
    print("rr1:", rr1.eval(m))
    print("rr2:", rr2.eval(m))
    print("rro:", rr.eval(m))
    print("h11:", h11.eval(m))
    print("h12:", h12.eval(m))
    print("h21:", h21.eval(m))
    print("h22:", h22.eval(m))


def test2():
    T = 12
    qs = 5
    s = Solver()
    s.set(unsat_core=True)

    h11 = SymbolicHistory.create("h11", [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    h12 = SymbolicHistory.create("h12", [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0])
    rr1 = RoundRobinScheduler("rr1", qs, [h11, h12])
    rr1.run()
    add_constrs(s, rr1)

    h21 = SymbolicHistory.create("h21", [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    h22 = SymbolicHistory.create("h22", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    rr2 = RoundRobinScheduler("rr2", qs, [h21, h22])
    rr2.run()
    add_constrs(s, rr2)

    rr = RoundRobinScheduler("rr", qs, [rr1.out, rr2.out])
    rr.run()
    add_constrs(s, rr)

    # for t in range(1, T):
    #     s.assert_and_track(Or(h11[t] == 0, h11[t] == 1), "h11[{}] = 0 | 1".format(t))
    #     s.assert_and_track(Or(h12[t] == 0, h12[t] == 2), "h12[{}] = 0 | 2".format(t))
    #     s.assert_and_track(Or(h21[t] == 0, h21[t] == 1), "h21[{}] = 0 | 1".format(t))
    #     s.assert_and_track(Or(h22[t] == 0, h22[t] == 2), "h22[{}] = 0 | 2".format(t))
    #
    s.assert_and_track(Or([ccount(rr.out, 1, t) - ccount(rr.out, 2, t) >= 4 for t in range(1, T)]), "starvation")

    print(s.check())
    m = s.model()
    print(rr1.eval(m))
    print(rr2.eval(m))
    print(rr.eval(m))
    print("h11:", h11.eval(m))
    print("h12:", h12.eval(m))
    print("h21:", h21.eval(m))
    print("h22:", h22.eval(m))


def test3():
    T = 20
    qs = 2
    s = SmtSolver()
    h1 = SymbolicHistory.create("h1", [0, 1, 2, 1, 2, 1, 2, 1, 2, 1], T)
    h2 = SymbolicHistory.create("h2", [0, 2, 1, 2, 1, 2, 1, 2, 1, 2], T)
    # h1 = SymbolicHistory.create("h1", [0, 1, 0, 2, 0, 1, 0, 2, 0, 1], T)
    # h2 = SymbolicHistory.create("h2", [0, 2, 0, 1, 0, 2, 0, 1, 0, 2], T)
    rr = RoundRobinScheduler("rr", T, qs, [h1, h2])
    rr.run()
    s.add_constrs(rr)
    m = s.check_sat()
    # print(rr.queues[0].eval_to_str(m))
    # print(rr.queues[1].eval_to_str(m))
    print(rr.eval(m))
    # print(rr.eval_to_str(m))


def main():
    # t()
    # test()
    # test2()
    test3()


if __name__ == '__main__':
    main()
