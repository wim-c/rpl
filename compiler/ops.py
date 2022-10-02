def unop_int(x):
    return ((x >> 8) & 0xff) | ((x & 0xff) << 8)

def unop_not(x):
    return x ^ 0xffff

def binop_mul(x, y):
    return x*y

def binop_add(x, y):
    return x + y

def binop_sub(x, y):
    return x - y

def binop_div(x, y):
    ay = abs(y)
    ax = x if x >= 0 else ay - x - 1

    q = ax//ay if ay != 0 else -1

    return q if (x < 0) == (y < 0) else -q

def binop_lt(x, y):
    return -1 if x < y else 0

def binop_leq(x, y):
    return -1 if x <= y else 0

def binop_neq(x, y):
    return -1 if x != y else 0

def binop_eq(x, y):
    return -1 if x == y else 0

def binop_gt(x, y):
    return -1 if x > y else 0

def binop_geq(x, y):
    return -1 if x >= y else 0

def binop_mod(x, y):
    ay = abs(y)
    ax = x if x >= 0 else ay - x - 1

    r = ax%ay if ay != 0 else ax

    return r if x >= 0 else ay - r - 1

def binop_and(x, y):
    return x & y

def binop_or(x, y):
    return x | y

def binop_xor(x, y):
    return x ^ y

unop_int.arity = 1
unop_not.arity = 1
binop_mul.arity = 2
binop_add.arity = 2
binop_sub.arity = 2
binop_div.arity = 2
binop_lt.arity = 2
binop_leq.arity = 2
binop_neq.arity = 2
binop_eq.arity = 2
binop_gt.arity = 2
binop_geq.arity = 2
binop_mod.arity = 2
binop_and.arity = 2
binop_or.arity = 2
binop_xor.arity = 2
