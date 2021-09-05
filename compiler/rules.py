
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('define_proc', None, 7), ('THEN', None, 1), ('ref', 3), ('expr', 5), ('word', 6), ('const', 2), ('END', None, 0), ('define_macro', None, 6), ('words', None, 16), ('contif', None, 3), ('symbol', None, 15), ('mark', 4), ('data', None, 4), ('compare', 1), ('program', None, 13), ('if', None, 8), ('macro', None, 10), ('define_data', None, 5), ('statements', None, 14), ('bytes', None, 2), ('proc_body', None, 12), ('label', None, 9), ('proc', None, 11)),
        (('not', None, 29),),
        (('ref', 8), ('expr', 9), ('word', 10), ('const', 7), ('unop', None, 19), ('branch', 0, 25)),
        (('ref', 8), ('expr', 9), ('word', 10), ('const', 7), ('unop', None, 19), ('branch', 0, 24, 25)),
        (('stop', 0, 27), ('mark', 4, 28), ('goto', 0, 26), ('return', 0, 27)),
        (('ref', 13), ('expr', 14), ('word', 15), ('const', 12), ('unop', None, 21), ('branch', 0, 25)),
        (('ref', 8), ('expr', 9), ('word', 11), ('const', 7), ('unop', None, 17), ('branch', 0, 25)),
        (('expr', 9), ('word', 10), ('ref', 8), ('const', 7), ('binop', None, 20), ('branch', 0, 25), ('unop', None, 19)),
        (('expr', 9), ('word', 10), ('ref', 8), ('const', 7), ('binop', None, 20), ('branch', 0, 24, 25), ('unop', None, 19)),
        (('expr', 14), ('word', 15), ('ref', 13), ('const', 12), ('binop', None, 20), ('branch', 0, 25), ('unop', None, 21)),
        (('expr', 9), ('word', 11), ('ref', 8), ('const', 7), ('binop', None, 20), ('branch', 0, 25), ('unop', None, 17)),
        (('expr', 9), ('word', 11), ('ref', 8), ('const', 7), ('binop', None, 18), ('branch', 0, 25), ('unop', None, 17)),
        (('expr', 9), ('word', 10), ('ref', 8), ('const', 7), ('binop', None, 23), ('branch', 0, 25), ('unop', None, 19)),
        (('expr', 9), ('word', 10), ('ref', 8), ('const', 7), ('binop', None, 23), ('branch', 0, 24, 25), ('unop', None, 19)),
        (('expr', 14), ('word', 15), ('ref', 13), ('const', 12), ('binop', None, 22), ('branch', 0, 25), ('unop', None, 21)),
        (('expr', 9), ('word', 11), ('ref', 8), ('const', 7), ('binop', None, 23), ('branch', 0, 25), ('unop', None, 17)),
    )

    order = {
        'unop': {'not', 'int'},
        'binop': {'-', 'or', 'compare', '/', '>=', '<>', '<', '+', '>', '\\', 'and', '<=', '=', '*'},
        'const': {'ref', 'word', 'expr'},
        'branch': {'goto', 'gosub'},
        'compare': {'>=', '<>', '<', '>', '<=', '='}
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
            owner.push_define_data,
            owner.push_define_macro,
            owner.push_define_proc,
            owner.push_if,
            owner.push_label,
            owner.push_macro,
            owner.push_proc,
            owner.push_proc_body,
            owner.push_program,
            owner.push_statements,
            owner.push_symbol,
            owner.push_words,
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
            owner.compare_not
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
