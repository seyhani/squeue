from symbolic.hist import SymbolicHistory, single_id_hist, create_hist
from symbolic.rl import RateLimiter
from symbolic.rr import RoundRobinScheduler
from symbolic.smt_solver import SmtSolver
from symbolic.util import exists, forall


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


def rr_rl():
    T = 20
    last_t = T - 1
    ht = int(T / 2)
    s = SmtSolver()
    h1 = single_id_hist("h1", T, 1)
    h2 = single_id_hist("h2", T, 2)
    rr = RoundRobinScheduler("rr", T, 5, [h1, h2])
    rl = RateLimiter("rl", T, 2, rr.out)
    out = rl.out

    p = [
        forall(lambda t: h1.czero(t) <= 2, range(ht)),
        forall(lambda t: h1[t] == 0, range(ht, T)),
        forall(lambda t: h2.czero(t) <= 2, range(ht)),
        forall(lambda t: h2[t] == 0, range(ht, T))
    ]

    p1 = [
        rr.out.min_gap(last_t) >= 1
    ]

    q = [
        exists(lambda t: out.ccount(t, 1) - out.ccount(t, 2) >= 3, range(T))
    ]

    rr.run()
    s.add_struct(rr)
    rl.run()
    s.add_struct(rl)

    s.add_constrs(p)
    s.add_constrs(p1)
    s.add_constrs(q)

    m = s.check_sat()

    print("h1: ", h1.eval(m))
    print("h2: ", h2.eval(m))
    print("rr: ", rr.eval(m))
    print("mg: ", [m.eval(rr.out.min_gap(t)) for t in range(T)])
    print("rl: ", rl.eval(m))


def main():
    # test()
    rr_rl()


if __name__ == '__main__':
    main()
