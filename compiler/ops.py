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
    if y == 0:
        return 1 if x < 0 else -1
    else:
        q, r = divmod(x, y)
        return q if r == 0 or q >= 0 else q + 1

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
    if y == 0:
        return x
    else:
        q, r = divmod(x, y)
        return r if r == 0 or q >= 0 else r - y

def binop_and(x, y):
    return x & y

def binop_or(x, y):
    return x | y
