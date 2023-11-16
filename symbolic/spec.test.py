from typing import List

from z3 import Or, IntVal, If, Xor, ArithRef, Not, And

from symbolic.hist import SymbolicHistory
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import exists, forall, ZERO, abs_expr


def ccount(hist: List[ArithRef], id: int, t: int):
    res = IntVal(0)
    for i in range(1, t):
        res += If(hist[i] == id, 1, 0)
    return res


def count(hist: List[ArithRef], id: int):
    res = IntVal(0)
    for h in hist:
        res += If(h == id, 1, 0)
    return res


def base_sepc():
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
    s.add_constr(forall(lambda t: Or(h11[t] > ZERO, h21[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: Or(h12[t] > ZERO, h22[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: h11[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h12[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h21[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h22[t] == 0, range(pc + 1, T)))

    sp1 = ccount(rr1.out, 1, T - 1) >= ccount(rr1.out, 2, T - 1)
    sp2 = ccount(rr2.out, 1, T - 1) >= ccount(rr1.out, 2, T - 1)
    sp3 = ccount(rr2.out, 2, T - 1) == 0
    sp = And(sp1, sp2, sp3)
    s.add_constr(sp)

    q = exists(lambda t: ccount(rro.out, 1, t) - ccount(rro.out, 2, t) >= 4, range(1, T))
    s.add_constr(Not(q))

    m = s.check_sat()
    print("h11: ", h11.eval(m))
    print("h12: ", h12.eval(m))
    print("h21: ", h21.eval(m))
    print("h22: ", h22.eval(m))
    print("rr1: ", rr1.out.eval(m))
    print("rr2: ", rr2.out.eval(m))
    print("rro: ", rro.out.eval(m))


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
    # s.add_constr(forall(lambda t: Xor(h11[t] > ZERO, h21[t] > ZERO), range(1, pc + 1)))
    # s.add_constr(forall(lambda t: Xor(h12[t] > ZERO, h22[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: Or(h11[t] > ZERO, h21[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: Or(h12[t] > ZERO, h22[t] > ZERO), range(1, pc + 1)))
    s.add_constr(forall(lambda t: h11[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h12[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h21[t] == 0, range(pc + 1, T)))
    s.add_constr(forall(lambda t: h22[t] == 0, range(pc + 1, T)))

    p1 = forall(lambda t: abs_expr(ccount(rr1.out, 1, t) - ccount(rr2.out, 2, t)) <= 1, range(1, T, 2))
    p2 = forall(lambda t: abs_expr(ccount(rr1.out, 2, t) - ccount(rr2.out, 1, t)) <= 1, range(1, T, 2))
    sp = And(p1, p2)
    s.add_constr(Not(sp))
    # Add not to the pre then summarize
    # p2 = Or(ccount(rr1.out, 2, T - 1) <= 1, ccount(rr2.out, 2, T - 1) <= 1)
    # p2 = exists(lambda t:
    #             ccount(rr1.out, 1, t) + ccount(rr2.out, 1, t) - ccount(rr1.out, 2, t) - ccount(rr2.out, 2, t) >= 4,
    #             range(1, T))
    # s.add_constr(Not(p2))
    # s.add_constr(ccount(rr2.out, 2, T - 1) == 0)
    # s.add_constr(Not(q))

    # sp = exists(lambda t: And(rr1.out[t] == 1, rr1.out[t + 1] == 1, rr2.out[t] == 1, rr2.out[t + 1] == 1),
    #             range(1, T - 1))
    # sp = exists(lambda t: count([rr1.out[t], rr1.out[t + 1], rr2.out[t], rr2.out[t + 1]], 1) >= 3,
    #             range(1, T - 1))

    q = exists(lambda t: ccount(rro.out, 1, t) - ccount(rro.out, 2, t) >= 4, range(1, T))
    s.add_constr(Not(q))

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




def main():
    test_dist()


if __name__ == '__main__':
    main()
