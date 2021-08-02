
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('statements', None, 13), ('beq', 1), ('word', 3), ('expr', 5), ('ref', 6), ('const', 2), ('if', None, 8), ('words', None, 15), ('THEN', None, 1), ('symbol', None, 14), ('define_macro', None, 6), ('macro', None, 10), ('gosub', 4), ('data', None, 4), ('program', None, 12), ('label', None, 9), ('contif', None, 3), ('END', None, 0), ('bytes', None, 2), ('define_proc', None, 7), ('define_data', None, 5), ('proc', None, 11), ('goto', 7)),
        (('goto', 17),),
        (('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26), ('word', 9), ('expr', 10), ('ref', 11), ('const', 8), ('unop', None, 20)),
        (('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26), ('word', 16), ('expr', 10), ('ref', 11), ('const', 8), ('unop', None, 18)),
        (('return', None, 27),),
        (('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26), ('word', 13), ('expr', 14), ('ref', 15), ('const', 12), ('unop', None, 22)),
        (('gosub', 4, 25, 26), ('goto', 7, 25, 26), ('branch', 0, 25, 26), ('word', 9), ('expr', 10), ('ref', 11), ('const', 8), ('unop', None, 20)),
        (('mark', 0, 17),),
        (('expr', 10), ('word', 9), ('ref', 11), ('const', 8), ('binop', None, 21), ('unop', None, 20), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 10), ('word', 16), ('ref', 11), ('const', 8), ('binop', None, 21), ('unop', None, 18), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 14), ('word', 13), ('ref', 15), ('const', 12), ('binop', None, 21), ('unop', None, 22), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 10), ('word', 9), ('ref', 11), ('const', 8), ('binop', None, 21), ('unop', None, 20), ('gosub', 4, 25, 26), ('goto', 7, 25, 26), ('branch', 0, 25, 26)),
        (('expr', 10), ('word', 9), ('ref', 11), ('const', 8), ('binop', None, 24), ('unop', None, 20), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 10), ('word', 16), ('ref', 11), ('const', 8), ('binop', None, 24), ('unop', None, 18), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 14), ('word', 13), ('ref', 15), ('const', 12), ('binop', None, 23), ('unop', None, 22), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('expr', 10), ('word', 9), ('ref', 11), ('const', 8), ('binop', None, 24), ('unop', None, 20), ('gosub', 4, 25, 26), ('goto', 7, 25, 26), ('branch', 0, 25, 26)),
        (('expr', 10), ('word', 16), ('ref', 11), ('const', 8), ('binop', None, 19), ('unop', None, 18), ('gosub', 4, 26), ('goto', 7, 26), ('branch', 0, 26)),
        (('mark', 0, 16, 17),),
    )

    order = {
        'unop': {'not', 'int'},
        'binop': {'\\', '<', '=', '-', 'or', '*', '>', '+', '<=', '<>', '>=', '/', 'and'},
        'const': {'expr', 'ref', 'word'},
        'branch': {'goto', 'gosub'}
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
            owner.push_program,
            owner.push_statements,
            owner.push_symbol,
            owner.push_words,
            owner.beq_goto_mark,
            owner.goto_mark,
            owner.word_unop,
            owner.word_word_binop,
            owner.const_unop,
            owner.const_const_binop,
            owner.expr_unop,
            owner.expr_expr_binop,
            owner.expr_const_binop,
            owner.ref_branch,
            owner.const_branch,
            owner.gosub_return
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
