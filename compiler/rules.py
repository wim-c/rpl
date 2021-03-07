
# This file is generated.  Do not edit.

class ParseStateMachine(object):
    transitions = (
        (('word', 1), ('expr', 2), ('label', None, 21), ('beq', 3), ('symbol', None, 23), ('<', 4), ('ref', 10), ('const', 5), ('>', 6), ('mark', 7), ('int', 8), ('jmp', 9), ('=', 11), ('macro', None, 22), ('<>', 12), ('>=', 13), ('<=', 14), ('%', 15), ('if', None, 19), ('not', 16)),
        (('word', 25), ('expr', 26), ('$', 0, 33), ('+', 0, 41), ('ref', 27), ('const', 28), ('int', None, 0), ('.', None, 35), ('and', 0, 44), ('-', 0, 42), ('^', 0, 39), ('/', 0, 43), ('#', None, 30), ('or', 0, 45), ('not', None, 1), ('unop', None, 27), ('*', 0, 40), ('if', None, 20), ('&', 0, 58), ('goto', 9, 58)),
        (('word', 29), ('expr', 30), ('ref', 31), ('const', 32), ('unop', None, 24), ('.', None, 35), ('#', None, 32), ('&', 0, 58), ('goto', 9, 58)),
        (('goto', 33),),
        (('not', None, 46),),
        (('word', 21), ('expr', 22), ('ref', 24), ('const', 23), ('unop', None, 27), ('.', None, 35), ('&', 0, 58), ('goto', 9, 58)),
        (('not', None, 51),),
        (('mark', None, 60), ('jmp', None, 59)),
        (('int', None, 57),),
        (('command', None, 61),),
        (('word', 17), ('expr', 18), ('ref', 20), ('const', 19), ('unop', None, 27), ('.', None, 35), ('#', None, 31), ('&', 0, 58), ('goto', 9, 58)),
        (('not', None, 48),),
        (('not', None, 49),),
        (('not', None, 50),),
        (('not', None, 47),),
        (('symmetric', None, 56), ('<', None, 52), ('>', None, 55), ('>=', None, 54), ('<=', None, 53), ('%', None, 57)),
        (('not', None, 57),),
        (('word', 25), ('expr', 26), ('and', None, 16, 29), ('or', None, 18, 29), ('binop', None, 29), ('ref', 27), ('#', None, 30), ('not', None, 1), ('int', None, 0), ('unop', None, 27), (';', None, 37), ('&', 0, 58), ('goto', 9, 58), ('$', 0, 33), ('.', None, 35), ('const', 28), ('^', 0, 39), ('%', None, 34), ('if', None, 20)),
        (('word', 29), ('expr', 30), ('binop', None, 28), ('ref', 31), ('#', None, 32), ('unop', None, 24), (';', None, 37), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 32), ('%', None, 34)),
        (('word', 21), ('expr', 22), ('binop', None, 29), ('ref', 24), ('unop', None, 27), (';', None, 37), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 23), ('%', None, 34)),
        (('word', 17), ('expr', 18), ('binop', None, 29), ('ref', 20), ('#', None, 31), ('unop', None, 27), (';', None, 37), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 19), ('%', None, 34)),
        (('word', 25), ('expr', 26), ('and', None, 16, 29), ('or', None, 18, 29), ('binop', None, 29), ('ref', 27), ('#', None, 30), ('not', None, 1), ('int', None, 0), ('unop', None, 27), ('&', 0, 58), ('goto', 9, 58), ('$', 0, 33), ('.', None, 35), ('const', 28), ('^', 0, 39), ('%', None, 34), ('if', None, 20)),
        (('word', 29), ('expr', 30), ('binop', None, 28), ('ref', 31), ('#', None, 32), ('unop', None, 24), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 32), ('%', None, 34)),
        (('word', 21), ('expr', 22), ('binop', None, 29), ('ref', 24), ('unop', None, 27), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 23), ('%', None, 34)),
        (('word', 17), ('expr', 18), ('binop', None, 29), ('ref', 20), ('#', None, 31), ('unop', None, 27), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 19), ('%', None, 34)),
        (('word', 25), ('expr', 26), ('<', None, 6), ('and', None, 13), ('/', None, 5), ('=', None, 9), ('or', None, 14), ('>=', None, 11), ('*', None, 2), ('+', None, 3), ('>', None, 10), ('-', None, 4), ('\\', None, 12), ('<>', None, 8), ('<=', None, 7), ('binop', None, 29), ('ref', 27), ('#', None, 30), ('not', None, 1), ('int', None, 0), ('unop', None, 27), (';', None, 36), ('&', 0, 58), ('goto', 9, 58), ('$', 0, 33), ('.', None, 35), ('const', 28), ('^', 0, 39), ('%', None, 34), ('if', None, 20)),
        (('word', 29), ('expr', 30), ('and', None, 15, 28), ('or', None, 17, 28), ('binop', None, 28), ('ref', 31), ('#', None, 32), ('unop', None, 24), (';', None, 36), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 32), ('%', None, 34)),
        (('word', 17), ('expr', 18), ('and', None, 15, 29), ('or', None, 17, 29), ('binop', None, 29), ('ref', 20), ('#', None, 31), ('unop', None, 27), (';', None, 36), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 19), ('%', None, 34)),
        (('word', 21), ('expr', 22), ('and', None, 15, 29), ('or', None, 17, 29), ('binop', None, 29), ('ref', 24), ('unop', None, 27), (';', None, 36), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 23), ('%', None, 34)),
        (('word', 25), ('expr', 26), ('binop', None, 26), ('ref', 27), ('#', None, 30), ('not', None, 1), ('int', None, 0), ('unop', None, 27), (';', None, 38), ('&', 0, 58), ('goto', 9, 58), ('$', 0, 33), ('.', None, 35), ('const', 28), ('^', 0, 39), ('%', None, 34), ('if', None, 20)),
        (('word', 29), ('expr', 30), ('binop', None, 25), ('ref', 31), ('#', None, 32), ('unop', None, 24), (';', None, 38), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 32), ('%', None, 34)),
        (('word', 17), ('expr', 18), ('binop', None, 26), ('ref', 20), ('#', None, 31), ('unop', None, 27), (';', None, 38), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 19), ('%', None, 34)),
        (('word', 21), ('expr', 22), ('binop', None, 26), ('ref', 24), ('unop', None, 27), (';', None, 38), ('&', 0, 58), ('goto', 9, 58), ('.', None, 35), ('const', 23), ('%', None, 34)),
        (('command', None, 61), ('mark', 7, 62))
    )

    order = {
        'command': {'clr', '<', 'and', '/', 'rnd', 'get', 'fn', 'peek', 'or', '=', '#', 'return', 'bne', '>=', 'sys', 'str$', '*', 'print', ';', '&', 'goto', 'not', 'beq', 'chr$', '@', 'input', '$', '+', 'poke', '.', '>', 'stop', 'int', '-', '^', 'next', '!', 'for', '\\', '<>', '<=', 'new', '%'},
        'unop': {'int', 'not'},
        'binop': {'or', '=', '\\', '<>', '+', '>=', '<', '<=', '>', '*', 'and', '/', '-'},
        'const': {'expr', 'word', 'ref'},
        'symmetric': {'or', '=', '<>', '+', '*', 'and'},
        'jmp': {'return', 'goto', 'stop'}
    }

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            owner.unop_int,
            owner.unop_not,
            owner.binop_mul,
            owner.binop_add,
            owner.binop_sub,
            owner.binop_div,
            owner.binop_lt,
            owner.binop_le,
            owner.binop_ne,
            owner.binop_eq,
            owner.binop_gt,
            owner.binop_ge,
            owner.binop_mod,
            owner.binop_and,
            owner.binop_or,
            owner.and_word_const,
            owner.and_const_word,
            owner.or_word_const,
            owner.or_const_word,
            owner.push_if,
            owner.push_if_word,
            owner.push_label,
            owner.push_macro,
            owner.push_symbol,
            owner.unop_expr,
            owner.binop_expr_expr,
            owner.binop_expr_const,
            owner.unop_const,
            owner.binop_const_expr,
            owner.binop_const_const,
            owner.dup_word,
            owner.dup_ref,
            owner.dup_expr,
            owner.rot_word,
            owner.swap_const,
            owner.drop_const,
            owner.over_word,
            owner.over_ref,
            owner.over_expr,
            owner.pick_word,
            owner.mul_word,
            owner.add_word,
            owner.sub_word,
            owner.div_word,
            owner.and_word,
            owner.or_word,
            owner.lt_not,
            owner.le_not,
            owner.eq_not,
            owner.neq_not,
            owner.ge_not,
            owner.gt_not,
            owner.lt_swap,
            owner.le_swap,
            owner.ge_swap,
            owner.gt_swap,
            owner.symmetric_swap,
            owner.cancel_two,
            owner.implied,
            owner.mark_jmp,
            owner.mark_mark,
            owner.jmp_skip,
            owner.beq_goto
        )

        self.state = 0

    @classmethod
    def get_transition(cls, state, subject):
        for transition in cls.transitions[state]:
            if cls.matches(transition[0], subject):
                return transition

    def process(self, subject):
        transition = self.get_transition(self.state, subject)
        if transition is None and self.state != 0:
            transition = self.get_transition(0, subject)

        if transition is None:
            state, self.state = self.state, 0
            return (state,)

        state, self.state = self.state, transition[1]
        return (state, *(self.methods[m] for m in transition[2:]))

    def goto(self, state):
        self.state = state
