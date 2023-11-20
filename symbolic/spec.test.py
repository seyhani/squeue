from z3 import And, Not, Or, Implies, Xor

from symbolic.hist import SymbolicHistory, single_id_hist, create_hist
from symbolic.rl import RateLimiter
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import exists, forall, abs_expr


def test():
    T = 20
    last_t = T - 1
    s = SmtSolver()
    h1 = create_hist("h1", [1, 2, 1, 2, 1, 2, 1, 2, 1, 2], T)
    rl = RateLimiter("rl", T, 2, h1)
    rl.run()
    s.add_struct(rl)

    m = s.check_sat()
    print(rl.queue.eval_to_str(m))
    print("h1: ", h1.eval(m))
    print("rl: ", rl.eval(m))


def bar():
    s = SmtSolver()
    h = create_hist("h1", [0, 1, 0, 1, 0, 1, 0, 1, 0, 0])
    s.add_struct(h)
    m = s.check_sat()
    # print(h.eval(m))
    h1 = h.project(1)
    # print(type(h1))
    # print(h1.eval(m))
    print(h1.eval_to_str(m))


def rr_rl():
    T = 25
    pc = 8
    ht = 3 * pc + 1
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    h2 = single_id_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])
    rl = RateLimiter("rl", T, 2, rr.out)
    out = rl.out

    p = And(
        h1.max_gap() <= 2,
        h1.ccount(1) >= 1,
        h1.ccount() >= pc,
        # forall(lambda t: h1[t] == 0, range(ht, T)),
        h2.max_gap() <= 2,
        h2.ccount(1) >= 1,
        h2.ccount() >= pc,
        # forall(lambda t: h2[t] == 0, range(ht, T)),
    )

    p1 = And(
        # forall(lambda t: Implies(And(rr.out[t - 1] > 0, rr.out[t] > 0), rr.out[t - 1] != rr.out[t]), range(1, T)),
        rr.out.project(1).max_gap() == 1,
        rr.out.project(1).min_gap() == 1,
        rr.out.max_gap() <= 0
    )

    q = And(
        exists(lambda t: abs_expr(out.project(1).ccount(t) - out.project(2).ccount(t)) >= 4, range(T)),
    )

    rr.run()
    s.add_struct(rr)
    rl.run()
    s.add_struct(rl)

    s.add_constr(p)
    s.add_constr(p1)
    # s.add_constr(Not(p1))
    # s.add_constr(q)
    s.add_constr(Not(q))

    m = s.check_sat()

    print("h1: ", h1.eval(m))
    print("h2: ", h2.eval(m))
    print("rr: ", rr.eval(m))
    print("rl: ", rl.eval(m))


def rr():
    T = 15
    pc = 6
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    h2 = single_id_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])

    p = And(
        h1.max_gap() <= 1,
        h1.ccount(1) >= 1,
        h1.ccount() >= pc,
        # forall(lambda t: h1[t] == 0, range(ht, T)),
        h2.max_gap() <= 1,
        h2.ccount(1) >= 1,
        h2.ccount() >= pc,
        # forall(lambda t: h2[t] == 0, range(ht, T)),
    )

    p1 = And(
        # forall(lambda t: Implies(And(rr.out[t - 1] > 0, rr.out[t] > 0), rr.out[t - 1] != rr.out[t]), range(1, T)),
        rr.out.project(1).max_gap() == 1,
        rr.out.project(1).min_gap() == 1,
        rr.out.max_gap() <= 0
    )

    rr.run()
    s.add_struct(rr)

    s.add_constr(p)
    # s.add_constr(p1)
    s.add_constr(Not(p1))

    m = s.check_sat()

    print("h1: ", h1.eval(m))
    print("h2: ", h2.eval(m))
    print("rr: ", rr.eval(m))


def main():
    # test()
    rr_rl()
    # rr()


if __name__ == '__main__':
    main()
