from z3 import Solver, Or, IntVal, If, And, Xor, Int

from symbolic.hist import SymbolicHistory
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver


def t():
    s = SmtSolver()
    h1 = SymbolicHistory("h1", 10)
    h2 = SymbolicHistory("h2", 10)
    rr = RoundRobinScheduler("rr1", 15, 3, [h1, h2])
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
    T = 12
    qs = 3
    s = SmtSolver()

    h11 = SymbolicHistory("h11", T)
    # s.add_struct(h11)
    h12 = SymbolicHistory("h12", T)
    # s.add_struct(h12)
    rr1 = RoundRobinScheduler("rr1", T, qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory("h21", T)
    # s.add_struct(h21)
    h22 = SymbolicHistory("h22", T)
    # s.add_struct(h22)
    rr2 = RoundRobinScheduler("rr2", T, qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rr = RoundRobinScheduler("rr", T, qs, [rr1.out, rr2.out])
    rr.run()
    s.add_struct(rr)

    for t in range(1, T):
        s.add_constr(Or(h11[t] == 0, h11[t] == 1))
        s.add_constr(Or(h21[t] == 0, h21[t] == 1))
        s.add_constr(Or(h12[t] == 0, h12[t] == 2))
        s.add_constr(Or(h22[t] == 0, h22[t] == 2))
        s.add_constr(Xor(h11[t] > 0, h21[t] > 0))
        s.add_constr(Xor(h12[t] > 0, h22[t] > 0))
    #
    s.add_constr(Or([And(rr.out[t] == 1, rr.out[t - 1] == 1, rr.out[t - 2] == 1) for t in range(2, T)]))
    m = s.check_sat()
    print("h11: ", h11.eval(m))
    print("h21: ", h21.eval(m))
    print("h12: ", h12.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rr.out.eval(m))


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
    s.add_struct(rr)
    m = s.check_sat()
    # print(rr.queues[0].eval_to_str(m))
    # print(rr.queues[1].eval_to_str(m))
    print(rr.eval(m))
    # print(rr.eval_to_str(m))


def main():
    # t()
    test()
    # test2()
    # test3()


if __name__ == '__main__':
    main()
