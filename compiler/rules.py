
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('label', None, 6), ('expr', 1), ('bytes', None, 2), ('macro', None, 9), ('let', 3, 7), ('data', None, 4), ('compare', 2), ('program', None, 11), ('THEN', None, 1), ('if', None, 5), ('ref', 5), ('word', 7), ('const', 4), ('proc', None, 10), ('mark', 6), ('contif', None, 3), ('symbol', None, 13), ('statements', None, 12), ('END', None, 0), ('literal', 0, 8)),
        (('expr', 13), ('#', None, 30), ('unop', None, 21), ('ref', 15), ('word', 16), ('const', 14), ('branch', 0, 25)),
        (('not', None, 29),),
        (('macro', None, 15), ('data', None, 14), ('proc', None, 16)),
        (('expr', 8), ('#', None, 30), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 24, 25)),
        (('return', 0, 27), ('stop', 0, 27), ('mark', 6, 28), ('goto', 0, 26)),
        (('expr', 8), ('#', None, 30), ('unop', None, 17), ('ref', 10), ('word', 12), ('const', 9), ('branch', 0, 25)),
        (('expr', 13), ('#', None, 30), ('%', None, 32), ('binop', None, 20), (';', None, 31), ('unop', None, 21), ('ref', 15), ('word', 16), ('const', 14), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 20), (';', None, 31), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 20), (';', None, 31), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 24, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 20), (';', None, 31), ('unop', None, 17), ('ref', 10), ('word', 12), ('const', 9), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 18), (';', None, 31), ('unop', None, 17), ('ref', 10), ('word', 12), ('const', 9), ('branch', 0, 25)),
        (('expr', 13), ('#', None, 30), ('%', None, 32), ('binop', None, 22), (';', None, 31), ('unop', None, 21), ('ref', 15), ('word', 16), ('const', 14), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 23), (';', None, 31), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 23), (';', None, 31), ('unop', None, 19), ('ref', 10), ('word', 11), ('const', 9), ('branch', 0, 24, 25)),
        (('expr', 8), ('#', None, 30), ('%', None, 32), ('binop', None, 23), (';', None, 31), ('unop', None, 17), ('ref', 10), ('word', 12), ('const', 9), ('branch', 0, 25)),
    )

    order = {
        'literal': {'float', 'chars', 'string'},
        'unop': {'not', 'int'},
        'binop': {'<=', '+', 'and', '-', '<', '<>', '=', '\\', '>=', '>', '/', '*', 'compare', 'or'},
        'const': {'expr', 'word', 'ref'},
        'branch': {'goto', 'gosub'},
        'compare': {'<=', '<', '<>', '>=', '>', '='}
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
