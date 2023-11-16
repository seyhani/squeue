from typing import List

from z3 import Solver, Or, IntVal, If, And, Xor, Int, Not, ArithRef

from symbolic.hist import SymbolicHistory
from symbolic.rl import RL
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import exists, forall, ZERO, abs_expr, memoize


def ccount(hist: List[ArithRef], id: int, t: int):
    res = IntVal(0)
    for i in range(1, t):
        res += If(hist[i] == id, 1, 0)
    return res


def cenq(hist: SymbolicHistory, t: int):
    res = IntVal(0)
    for i in range(1, t):
        res += If(hist[i] > 0, 1, 0)
    return res


@memoize
def zero_rank(hist: SymbolicHistory, t):
    if t == 0:
        return ZERO
    return If(hist[t] == 0, zero_rank(hist, t - 1) + 1, ZERO)


@memoize
def aipg(hist: SymbolicHistory, t):
    if t == 0:
        return ZERO
    return If(zero_rank(hist, t) == 0, zero_rank(hist, t - 1) + 1, 0)


def test_rr_composition():
    T = 12
    qs = 5
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

    rro = RoundRobinScheduler("rr", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    for t in range(1, T):
        s.add_constr(Or(h11[t] == 0, h11[t] == 1))
        s.add_constr(Or(h21[t] == 0, h21[t] == 1))
        s.add_constr(Or(h12[t] == 0, h12[t] == 2))
        s.add_constr(Or(h22[t] == 0, h22[t] == 2))
        s.add_constr(Or(h11[t] > 0, h21[t] > 0))
        s.add_constr(Or(h12[t] > 0, h22[t] > 0))

    p1 = forall(lambda t: ccount(rr1.out, 1, t) >= ccount(rr1.out, 2, t), range(1, T))
    p2 = forall(lambda t: ccount(rr2.out, 1, t) >= ccount(rr1.out, 2, t), range(1, T))
    p3 = ccount(rr2.out, 2, T) <= 0
    s.add_constrs([p1, p2, p3])

    q = exists(lambda t: ccount(rro.out, 1, t) - ccount(rro.out, 2, t) >= 4, range(1, T))
    s.add_constr(q)
    # s.add_constr(Not(q))
    # s.add_constr(exists(lambda t: rr.out[t] == 0, 3, T))
    # s.add_constr(Or([) for t in range(2, T)]))
    m = s.check_sat()
    print("h11: ", h11.eval(m))
    print("h12: ", h12.eval(m))
    print("h21: ", h21.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rro.out.eval(m))


def test_fairness_drop():
    T = 20
    qs = 4
    s = SmtSolver()

    h11 = SymbolicHistory.create("h11", [0, 0, 1, 1, 0, 0, 0, 1, 0, 1], T)
    h12 = SymbolicHistory.create("h12", [0, 0, 2, 0, 2, 0, 2, 0, 2, 0], T)
    rr1 = RoundRobinScheduler("rr1", T, 2 * qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory.create("h21", [0, 0, 1, 0, 1, 0, 1, 0, 1, 0], T)
    h22 = SymbolicHistory.create("h22", [0, 2, 0, 2, 0, 2, 0, 2, 0, 2], T)
    rr2 = RoundRobinScheduler("rr2", T, 2 * qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rro", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    m = s.check_sat()
    print(rro.queues[0].eval_to_str(m))
    print(rro.queues[1].eval_to_str(m))
    print("rr1:", rr1.eval(m))
    print("rr2:", rr2.eval(m))
    print("rro:", rro.eval(m))


def test_fairness_nodrop():
    T = 20
    qs = 2
    s = SmtSolver()

    h11 = SymbolicHistory.create("h11", [0, 1, 1, 1, 1, 1, 1, 1, 1, 1], T)
    h12 = SymbolicHistory.create("h12", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], T)
    rr1 = RoundRobinScheduler("rr1", T, 2 * qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory.create("h21", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], T)
    h22 = SymbolicHistory.create("h22", [0, 2, 2, 2, 2, 2, 2, 2, 2, 2], T)
    rr2 = RoundRobinScheduler("rr2", T, 2 * qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rro", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    m = s.check_sat()
    print(rro.queues[0].eval_to_str(m))
    print(rro.queues[1].eval_to_str(m))
    print("rr1:", rr1.eval(m))
    print("rr2:", rr2.eval(m))
    print("rro:", rro.eval(m))


def test_dist():
    pc = 6
    T = 2 * pc + 3
    qs = 5
    s = SmtSolver()

    h11 = SymbolicHistory("h11", T)
    h12 = SymbolicHistory("h12", T)
    rr1 = RoundRobinScheduler("rr1", T, qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory("h21", T)
    h22 = SymbolicHistory("h22", T)
    rr2 = RoundRobinScheduler("rr2", T, qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rro", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    s.add_constr(forall(lambda t: Or(h11[t] == 0, h11[t] == 1), range(1, T)))
    s.add_constr(forall(lambda t: Or(h21[t] == 0, h21[t] == 1), range(1, T)))
    s.add_constr(forall(lambda t: Or(h12[t] == 0, h12[t] == 2), range(1, T)))
    s.add_constr(forall(lambda t: Or(h22[t] == 0, h22[t] == 2), range(1, T)))
    s.add_constr(forall(lambda t: Xor(h11[t] > ZERO, h21[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: Xor(h12[t] > ZERO, h22[t] > ZERO), range(1, pc + 1)))
    # s.add_constr(forall(lambda t: Or(h11[t] > ZERO, h21[t] > ZERO), range(1, pc + 1)))
    # s.add_constr(forall(lambda t: Or(h12[t] > ZERO, h22[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: h11[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h12[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h21[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h22[t] == 0, range(pc + 1, T)))

    # p1 = forall(lambda t: abs_expr(ccount(rr1.out, 1, t) - ccount(rr1.out, 2, t)) <= 1, range(1, T, 2))
    # s.add_constr(Not(p1))
    # Add not to the pre then summarize
    # p2 = Or(ccount(rr1.out, 2, T - 1) <= 1, ccount(rr2.out, 2, T - 1) <= 1)
    # p2 = exists(lambda t:
    #             ccount(rr1.out, 1, t) + ccount(rr2.out, 1, t) - ccount(rr1.out, 2, t) - ccount(rr2.out, 2, t) >= 4,
    #             range(1, T))
    # s.add_constr(Not(p2))
    # s.add_constr(ccount(rr2.out, 2, T - 1) == 0)

    # q = exists(lambda t: ccount(rro.out, 1, t) - ccount(rro.out, 2, t) >= 4, range(1, T))
    # s.add_constr(q)
    # s.add_constr(Not(q))

    # sp = exists(lambda t: And(rr1.out[t] == 1, rr1.out[t + 1] == 1, rr2.out[t] == 1, rr2.out[t + 1] == 1),
    #             range(1, T - 1))
    sp = exists(lambda t: ccount([rr1.out[t], rr1.out[t + 1], rr2.out[t], rr2.out[t + 1]], 1, t),
                range(1, T - 1))
    s.add_constr(sp)

    # s.add_constr(forall(lambda t: ccount(rr1.out, 1, t) == ccount(rr2.out, 2, t), range(1, T, 4)))
    # s.add_constr(forall(lambda t: ccount(rr1.out, 2, t) == ccount(rr2.out, 1, t), range(1, T, 4)))
    # s.add_constr(ccount(rr1.out, 2, T) == ccount(rr2.out, 1, T))
    # s.add_constr(exists(lambda t: And([rro.out[i] == 1 for i in range(t, t + pc)]), range(1, T)))
    # s.add_constr(exists(lambda t: rro.out[t] == 0, 3, T))
    # s.add_constr(Or([) for t in range(2, T)]))

    m = s.check_sat()
    print("h11: ", h11.eval(m))
    print("h12: ", h12.eval(m))
    print("h21: ", h21.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rro.out.eval(m))


def test_spec():
    T = 12
    qs = 5
    s = SmtSolver()

    h11 = SymbolicHistory("h11", T)
    h12 = SymbolicHistory("h12", T)
    rr1 = RoundRobinScheduler("rr1", T, 2 * qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory("h21", T)
    h22 = SymbolicHistory("h22", T)
    rr2 = RoundRobinScheduler("rr2", T, qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rro", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    for t in range(1, T):
        s.add_constr(Or(h11[t] == 0, h11[t] == 1))
        s.add_constr(Or(h21[t] == 0, h21[t] == 1))
        s.add_constr(Or(h12[t] == 0, h12[t] == 2))
        s.add_constr(Or(h22[t] == 0, h22[t] == 2))
        s.add_constr(Xor(h11[t] > 0, h21[t] > 0))
        s.add_constr(Xor(h12[t] > 0, h22[t] > 0))

    s.add_constr(ccount(rr2.out, 2, T) == 0)
    s.add_constr(forall(lambda t: ccount(rr1.out, 2, t) == ccount(rr2.out, 1, t), 1, T))
    query = exists(lambda t: And(rro.out[t] == 1, rro.out[t - 1] == 1, rro.out[t - 2] == 1), 1, T)
    s.add_constr(Not(query))

    m = s.check_sat()
    print(m.eval(ccount(rr1.out, 1, T)))
    print(m.eval(ccount(rr1.out, 2, T)))
    print(m.eval(ccount(rr2.out, 1, T)))
    print(m.eval(ccount(rr2.out, 2, T)))
    # print(rro.queues[0].eval_to_str(m))
    # print(rro.queues[1].eval_to_str(m))
    print("h11: ", h11.eval(m))
    print("h12: ", h12.eval(m))
    print("h21: ", h21.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rro.out.eval(m))


def test_rl():
    pc = 4
    T = 20
    qs = 2
    s = SmtSolver()

    # h1 = SymbolicHistory.create("h1", [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], T)
    h1 = SymbolicHistory("h1", T)
    # h2 = SymbolicHistory.create("h2", [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2], T)
    h2 = SymbolicHistory("h2", T)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])
    rr.run()
    s.add_struct(rr)

    rl = RL("rl", T, qs, rr.out)
    rl.run()
    s.add_struct(rl)

    s.add_constr(forall(lambda t: Or(h1[t] == 0, h1[t] == 1), range(1, T)))
    s.add_constr(forall(lambda t: Or(h2[t] == 0, h2[t] == 2), range(1, T)))
    s.add_constr(forall(lambda t: And(rr.out[t - 1] > 0, rr.out[t] == 0), range(3, T, 2)))
    # s.add_constr(forall(lambda t: ccount(h1, 1, t) >= t / 2, range(2, 2 + pc * 2, 2)))
    # s.add_constr(forall(lambda t: ccount(h2, 2, t) >= t / 2, range(2, 2 + pc * 2, 2)))
    s.add_constr(ccount(h1, 1, T) >= pc)
    s.add_constr(ccount(h2, 2, T) >= pc)

    # q = exists(lambda t: ccount(rl.out, 2, t) - ccount(rl.out, 1, t) >= 4, range(1, T))
    # s.add_constr(Not(q))
    # s.add_constr(q)

    m = s.check_sat()
    print("h1: ", h1.eval(m))
    print("h2: ", h2.eval(m))
    print("rr: ", rr.eval(m))
    print("rl: ", rl.eval(m))


def new_test():
    pc = 6
    T = 2 * pc + 3
    qs = 5
    s = SmtSolver()

    h11 = SymbolicHistory("h11", T)
    h12 = SymbolicHistory("h12", T)
    rr1 = RoundRobinScheduler("rr1", T, qs, [h11, h12])
    rr1.run()
    s.add_struct(rr1)

    h21 = SymbolicHistory("h21", T)
    h22 = SymbolicHistory("h22", T)
    rr2 = RoundRobinScheduler("rr2", T, qs, [h21, h22])
    rr2.run()
    s.add_struct(rr2)

    rro = RoundRobinScheduler("rro", T, qs, [rr1.out, rr2.out])
    rro.run()
    s.add_struct(rro)

    s.add_constr(forall(lambda t: Or(h11[t] == 0, h11[t] == 1), range(1, T)))
    s.add_constr(forall(lambda t: Or(h21[t] == 0, h21[t] == 1), range(1, T)))
    s.add_constr(forall(lambda t: Or(h12[t] == 0, h12[t] == 2), range(1, T)))
    s.add_constr(forall(lambda t: Or(h22[t] == 0, h22[t] == 2), range(1, T)))
    s.add_constr(ccount(h11, 1, T) + ccount(h21, 1, T) >= pc)
    s.add_constr(ccount(h12, 2, T) + ccount(h22, 2, T) >= pc)

    p1 = forall(lambda t: aipg(rr1.out, t) <= 1, range(3, T))
    p2 = forall(lambda t: aipg(rr2.out, t) <= 1, range(3, T))

    s.add_constrs([p1, p2])

    q = exists(lambda t: ccount(rro.out, 1, t) - ccount(rro.out, 2, t) >= 4, range(1, T))
    s.add_constr(q)
    # s.add_constr(Not(q))

    m = s.check_sat()
    print("h11: ", h11.eval(m))
    print("h12: ", h12.eval(m))
    print("h21: ", h21.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rro.out.eval(m))


def main():
    # test_rl()
    # t()
    # test()
    # test2()
    test_rr_composition()
    # new_test()
    # test_fairness_nodrop()
    # test_dist()
    # test_spec()


if __name__ == '__main__':
    main()
