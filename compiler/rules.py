
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('expr', 1), ('END', None, 0), ('THEN', None, 1), ('define_proc', None, 7), ('if', None, 8), ('proc', None, 11), ('program', None, 12), ('define_macro', None, 6), ('label', None, 9), ('word', 3), ('const', 2), ('data', None, 4), ('goto', 4), ('beq', 5), ('bytes', None, 2), ('words', None, 15), ('define_data', None, 5), ('symbol', None, 14), ('statements', None, 13), ('macro', None, 10), ('contif', None, 3)),
        (('expr', 9), ('unop', None, 22), ('word', 11), ('const', 10)),
        (('expr', 6), ('unop', None, 20), ('word', 13), ('const', 7)),
        (('expr', 6), ('unop', None, 18), ('word', 8), ('const', 7)),
        (('mark', 0, 17),),
        (('goto', 12),),
        (('expr', 9), ('binop', None, 21), ('unop', None, 22), ('word', 11), ('const', 10)),
        (('expr', 6), ('binop', None, 21), ('unop', None, 20), ('word', 13), ('const', 7)),
        (('expr', 6), ('binop', None, 19), ('unop', None, 18), ('word', 8), ('const', 7)),
        (('expr', 9), ('binop', None, 23), ('unop', None, 22), ('word', 11), ('const', 10)),
        (('expr', 6), ('binop', None, 24), ('unop', None, 20), ('word', 13), ('const', 7)),
        (('expr', 6), ('binop', None, 24), ('unop', None, 18), ('word', 8), ('const', 7)),
        (('mark', 0, 16, 17),),
        (('expr', 6), ('binop', None, 21), ('unop', None, 18), ('word', 8), ('const', 7)),
    )

    order = {
        'unop': {'not', 'int'},
        'binop': {'-', '/', '<=', 'or', '*', '>', '<>', '=', '<', '>=', '+', '\\', 'and'},
        'const': {'word', 'expr', 'ref'}
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
            owner.beq_to_bne,
            owner.zero_offset_goto,
            owner.word_unop,
            owner.word_word_binop,
            owner.const_unop,
            owner.const_const_binop,
            owner.expr_unop,
            owner.expr_expr_binop,
            owner.expr_const_binop
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
