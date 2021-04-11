
# This file is generated.  Do not edit.

class ParseStateMachine(object):
    transitions = (
        (('>', 1), ('macro', None, 22), ('mark', 2), ('<>', 3), ('not', 4), ('jmp', 5), ('expr', 6), ('beq', 7), ('int', 8), ('label', None, 21), ('%', 9), ('<', 10), ('symbol', None, 23), ('ref', 11), ('<=', 12), ('=', 13), ('if', None, 19), ('&', 14), ('>=', 15), ('word', 17), ('const', 16)),
        (('not', None, 51),),
        (('mark', None, 60), ('jmp', None, 59)),
        (('not', None, 49),),
        (('not', None, 57),),
        (('command', None, 62),),
        (('unop', None, 24), ('goto', 5, 58), ('expr', 22), ('#', None, 32), ('ref', 23), ('&', 14, 58), ('word', 25), ('const', 24), ('.', None, 35)),
        (('goto', 34),),
        (('int', None, 57),),
        (('>', None, 55), ('symmetric', None, 56), ('%', None, 57), ('<', None, 52), ('<=', None, 53), ('>=', None, 54)),
        (('not', None, 46),),
        (('unop', None, 27), ('goto', 5, 58), ('expr', 18), ('#', None, 31), ('ref', 19), ('&', 14, 58), ('word', 21), ('const', 20), ('.', None, 35)),
        (('not', None, 47),),
        (('not', None, 48),),
        (('return', None, 61),),
        (('not', None, 50),),
        (('unop', None, 27), ('goto', 5, 58), ('expr', 26), ('ref', 27), ('&', 14, 58), ('word', 29), ('const', 28), ('.', None, 35)),
        (('.', None, 35), ('expr', 30), ('if', None, 20), ('^', 0, 39), ('$', 0, 33), ('not', None, 1), ('/', 0, 43), ('goto', 5, 58), ('int', None, 0), ('unop', None, 27), ('and', 0, 44), ('#', None, 30), ('*', 0, 40), ('ref', 31), ('-', 0, 42), ('&', 14, 58), ('or', 0, 45), ('word', 33), ('const', 32), ('+', 0, 41)),
        (('binop', None, 28), ('expr', 22), ('%', None, 34), (';', None, 37), ('unop', None, 24), ('goto', 5, 58), ('#', None, 32), ('ref', 23), ('&', 14, 58), ('word', 25), ('const', 24), ('.', None, 35)),
        (('binop', None, 29), ('expr', 18), ('%', None, 34), (';', None, 37), ('unop', None, 27), ('goto', 5, 58), ('#', None, 31), ('ref', 19), ('&', 14, 58), ('word', 21), ('const', 20), ('.', None, 35)),
        (('binop', None, 29), ('expr', 26), ('%', None, 34), (';', None, 37), ('unop', None, 27), ('goto', 5, 58), ('ref', 27), ('&', 14, 58), ('word', 29), ('const', 28), ('.', None, 35)),
        (('and', None, 16, 29), ('or', None, 18, 29), ('binop', None, 29), ('.', None, 35), ('expr', 30), ('%', None, 34), ('if', None, 20), (';', None, 37), ('^', 0, 39), ('$', 0, 33), ('not', None, 1), ('goto', 5, 58), ('int', None, 0), ('unop', None, 27), ('#', None, 30), ('ref', 31), ('&', 14, 58), ('word', 33), ('const', 32)),
        (('binop', None, 25), ('expr', 22), ('%', None, 34), (';', None, 38), ('unop', None, 24), ('goto', 5, 58), ('#', None, 32), ('ref', 23), ('&', 14, 58), ('word', 25), ('const', 24), ('.', None, 35)),
        (('binop', None, 26), ('expr', 18), ('%', None, 34), (';', None, 38), ('unop', None, 27), ('goto', 5, 58), ('#', None, 31), ('ref', 19), ('&', 14, 58), ('word', 21), ('const', 20), ('.', None, 35)),
        (('binop', None, 26), ('expr', 26), ('%', None, 34), (';', None, 38), ('unop', None, 27), ('goto', 5, 58), ('ref', 27), ('&', 14, 58), ('word', 29), ('const', 28), ('.', None, 35)),
        (('binop', None, 26), ('.', None, 35), ('expr', 30), ('%', None, 34), ('if', None, 20), (';', None, 38), ('^', 0, 39), ('$', 0, 33), ('not', None, 1), ('goto', 5, 58), ('int', None, 0), ('unop', None, 27), ('#', None, 30), ('ref', 31), ('&', 14, 58), ('word', 33), ('const', 32)),
        (('binop', None, 28), ('expr', 22), ('%', None, 34), ('unop', None, 24), ('goto', 5, 58), ('#', None, 32), ('ref', 23), ('&', 14, 58), ('word', 25), ('const', 24), ('.', None, 35)),
        (('binop', None, 29), ('expr', 18), ('%', None, 34), ('unop', None, 27), ('goto', 5, 58), ('#', None, 31), ('ref', 19), ('&', 14, 58), ('word', 21), ('const', 20), ('.', None, 35)),
        (('binop', None, 29), ('expr', 26), ('%', None, 34), ('unop', None, 27), ('goto', 5, 58), ('ref', 27), ('&', 14, 58), ('word', 29), ('const', 28), ('.', None, 35)),
        (('and', None, 16, 29), ('or', None, 18, 29), ('binop', None, 29), ('.', None, 35), ('expr', 30), ('%', None, 34), ('if', None, 20), ('^', 0, 39), ('$', 0, 33), ('not', None, 1), ('goto', 5, 58), ('int', None, 0), ('unop', None, 27), ('#', None, 30), ('ref', 31), ('&', 14, 58), ('word', 33), ('const', 32)),
        (('and', None, 15, 28), ('or', None, 17, 28), ('binop', None, 28), ('expr', 22), ('%', None, 34), (';', None, 36), ('unop', None, 24), ('goto', 5, 58), ('#', None, 32), ('ref', 23), ('&', 14, 58), ('word', 25), ('const', 24), ('.', None, 35)),
        (('and', None, 15, 29), ('or', None, 17, 29), ('binop', None, 29), ('expr', 18), ('%', None, 34), (';', None, 36), ('unop', None, 27), ('goto', 5, 58), ('#', None, 31), ('ref', 19), ('&', 14, 58), ('word', 21), ('const', 20), ('.', None, 35)),
        (('and', None, 15, 29), ('or', None, 17, 29), ('binop', None, 29), ('expr', 26), ('%', None, 34), (';', None, 36), ('unop', None, 27), ('goto', 5, 58), ('ref', 27), ('&', 14, 58), ('word', 29), ('const', 28), ('.', None, 35)),
        (('>', None, 10), ('expr', 30), ('<', None, 6), ('<=', None, 7), ('=', None, 9), ('+', None, 3), ('<>', None, 8), ('/', None, 5), ('and', None, 13), ('*', None, 2), ('-', None, 4), ('or', None, 14), ('>=', None, 11), ('\\', None, 12), ('binop', None, 29), ('%', None, 34), ('if', None, 20), (';', None, 36), ('^', 0, 39), ('$', 0, 33), ('not', None, 1), ('goto', 5, 58), ('int', None, 0), ('unop', None, 27), ('#', None, 30), ('ref', 31), ('&', 14, 58), ('word', 33), ('const', 32), ('.', None, 35)),
        (('command', None, 62), ('mark', 2, 63))
    )

    order = {
        'command': {'>', 'get', 'beq', 'new', '%', 'rnd', 'chr$', 'str$', '<', 'clr', '<=', '=', 'fn', 'sys', 'input', ';', '^', '+', '!', '$', '@', '<>', 'goto', '/', 'not', 'peek', 'and', '*', '#', 'int', 'next', 'poke', 'stop', '-', '&', 'or', 'return', 'for', 'bne', '>=', '\\', 'print', '.'},
        'unop': {'int', 'not'},
        'binop': {'>', '<', 'and', '<>', '-', '/', '<=', '=', 'or', '>=', '*', '\\', '+'},
        'const': {'expr', 'ref', 'word'},
        'symmetric': {'<>', '=', 'or', 'and', '*', '+'},
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
            owner.call_return,
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
