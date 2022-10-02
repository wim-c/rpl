
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('literal', 0, 8), ('symbol', None, 13), ('program', None, 11), ('let', 2, 7), ('mark', 3), ('expr', 4), ('macro', None, 9), ('word', 6), ('ref', 7), ('const', 5), ('label', None, 6), ('bytes', None, 2), ('proc', None, 10), ('data', None, 4), ('END', None, 0), ('THEN', None, 1), ('if', None, 5), ('compare', 1), ('statements', None, 12), ('contif', None, 3)),
        (('not', None, 29),),
        (('macro', None, 15), ('proc', None, 16), ('data', None, 14)),
        (('goto', 0, 26), ('mark', 3, 28), ('return', 0, 27), ('stop', 0, 27)),
        (('dup', None, 30), ('expr', 12), ('word', 14), ('ref', 15), ('const', 13), ('branch', 0, 25), ('unop', None, 21)),
        (('dup', None, 30), ('expr', 8), ('word', 10), ('ref', 11), ('const', 9), ('branch', 0, 25), ('unop', None, 19)),
        (('dup', None, 30), ('expr', 8), ('word', 16), ('ref', 11), ('const', 9), ('branch', 0, 25), ('unop', None, 17)),
        (('dup', None, 30), ('expr', 8), ('word', 10), ('ref', 11), ('const', 9), ('branch', 0, 24, 25), ('unop', None, 19)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 12), ('ref', 15), ('word', 14), ('const', 13), ('branch', 0, 25), ('unop', None, 21), ('binop', None, 20)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 10), ('const', 9), ('branch', 0, 25), ('unop', None, 19), ('binop', None, 20)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 16), ('const', 9), ('branch', 0, 25), ('unop', None, 17), ('binop', None, 20)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 10), ('const', 9), ('branch', 0, 24, 25), ('unop', None, 19), ('binop', None, 20)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 12), ('ref', 15), ('word', 14), ('const', 13), ('branch', 0, 25), ('unop', None, 21), ('binop', None, 22)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 10), ('const', 9), ('branch', 0, 25), ('unop', None, 19), ('binop', None, 23)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 16), ('const', 9), ('branch', 0, 25), ('unop', None, 17), ('binop', None, 23)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 10), ('const', 9), ('branch', 0, 24, 25), ('unop', None, 19), ('binop', None, 23)),
        (('swap', None, 32), ('dup', None, 30), ('over', None, 31), ('expr', 8), ('ref', 11), ('word', 16), ('const', 9), ('branch', 0, 25), ('unop', None, 17), ('binop', None, 18)),
    )

    order = {
        'literal': {'float', 'chars', 'string'},
        'unop': {'int', 'not'},
        'binop': {'and', '+', '<>', '>=', '*', '<', '/', 'mod', '>', '<=', 'or', 'xor', 'compare', '-', '='},
        'const': {'ref', 'word', 'expr'},
        'branch': {'goto', 'gosub'},
        'compare': {'<>', '>=', '<', '>', '<=', '='}
    }

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            owner.push_END,
            owner.push_THEN,
            owner.push_bytes,
            owner.push_contif,
            owner.push_data,
            owner.push_if,
            owner.push_label,
            owner.push_let,
            owner.push_literal,
            owner.push_macro,
            owner.push_proc,
            owner.push_program,
            owner.push_statements,
            owner.push_symbol,
            owner.let_data,
            owner.let_macro,
            owner.let_proc,
            owner.word_unop,
            owner.word_word_binop,
            owner.const_unop,
            owner.const_const_binop,
            owner.expr_unop,
            owner.expr_expr_binop,
            owner.expr_const_binop,
            owner.ref_branch,
            owner.const_branch,
            owner.mark_goto,
            owner.mark_final,
            owner.mark_mark,
            owner.compare_not,
            owner.const_dup,
            owner.const_const_over,
            owner.const_const_swap
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
