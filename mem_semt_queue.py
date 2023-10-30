from smt_queue import SmtQueue


class MemSmtQueue(SmtQueue):
    def __init__(self, name, hist):
        super().__init__(name, hist)
        self.head_exprs = {}
        self.blog_exprs = {}

    def tail(self, t, i):
        if (t, i) in self.head_exprs:
            return self.head_exprs[(t, i)]
        else:
            expr = super().tail(t, i)
            self.head_exprs[(t, i)] = expr
            return expr

    def blog(self, t):
        if t in self.blog_exprs:
            return self.blog_exprs[t]
        else:
            expr = super().blog(t)
            self.blog_exprs[t] = expr
            return expr
