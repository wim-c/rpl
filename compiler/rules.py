
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('expr', 1), ('mark', 2), ('compare', 3), ('define_data', None, 5), ('define_proc', None, 7), ('word', 4), ('statements', None, 13), ('data', None, 4), ('THEN', None, 1), ('if', None, 8), ('contif', None, 3), ('define_macro', None, 6), ('END', None, 0), ('ref', 5), ('words', None, 15), ('proc', None, 11), ('bytes', None, 2), ('const', 6), ('program', None, 12), ('symbol', None, 14), ('macro', None, 10), ('label', None, 9)),
        (('expr', 12), ('branch', 0, 24), ('unop', None, 20), ('word', 13), ('ref', 14), ('const', 15)),
        (('mark', 2, 27), ('goto', 0, 25), ('return', 0, 26)),
        (('not', None, 28),),
        (('expr', 7), ('branch', 0, 24), ('unop', None, 16), ('word', 8), ('ref', 9), ('const', 10)),
        (('expr', 7), ('branch', 0, 23, 24), ('unop', None, 18), ('word', 11), ('ref', 9), ('const', 10)),
        (('expr', 7), ('branch', 0, 24), ('unop', None, 18), ('word', 11), ('ref', 9), ('const', 10)),
        (('expr', 12), ('branch', 0, 24), ('binop', None, 19), ('unop', None, 20), ('ref', 14), ('word', 13), ('const', 15)),
        (('expr', 7), ('branch', 0, 24), ('binop', None, 17), ('unop', None, 16), ('ref', 9), ('word', 8), ('const', 10)),
        (('expr', 7), ('branch', 0, 23, 24), ('binop', None, 19), ('unop', None, 18), ('ref', 9), ('word', 11), ('const', 10)),
        (('expr', 7), ('branch', 0, 24), ('binop', None, 19), ('unop', None, 18), ('ref', 9), ('word', 11), ('const', 10)),
        (('expr', 7), ('branch', 0, 24), ('binop', None, 19), ('unop', None, 16), ('ref', 9), ('word', 8), ('const', 10)),
        (('expr', 12), ('branch', 0, 24), ('binop', None, 21), ('unop', None, 20), ('ref', 14), ('word', 13), ('const', 15)),
        (('expr', 7), ('branch', 0, 24), ('binop', None, 22), ('unop', None, 16), ('ref', 9), ('word', 8), ('const', 10)),
        (('expr', 7), ('branch', 0, 23, 24), ('binop', None, 22), ('unop', None, 18), ('ref', 9), ('word', 11), ('const', 10)),
        (('expr', 7), ('branch', 0, 24), ('binop', None, 22), ('unop', None, 18), ('ref', 9), ('word', 11), ('const', 10)),
    )

    order = {
        'unop': {'int', 'not'},
        'binop': {'<>', '>=', '\\', '/', '+', '*', '=', '-', '>', '<=', '<', 'and', 'or'},
        'const': {'expr', 'word', 'ref'},
        'branch': {'gosub', 'goto'},
        'compare': {'<>', '>=', '=', '>', '<=', '<'}
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
