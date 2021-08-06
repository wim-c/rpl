
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('bytes', None, 2), ('proc', None, 11), ('statements', None, 13), ('word', 1), ('END', None, 0), ('ref', 2), ('define_proc', None, 7), ('define_macro', None, 6), ('contif', None, 3), ('if', None, 8), ('goto', 3), ('words', None, 15), ('macro', None, 10), ('label', None, 9), ('symbol', None, 14), ('mark', 4), ('THEN', None, 1), ('define_data', None, 5), ('beq', 5), ('gosub', 6), ('expr', 7), ('program', None, 12), ('data', None, 4), ('const', 8)),
        (('word', 13), ('unop', None, 18), ('ref', 10), ('goto', 3, 26), ('gosub', 6, 26), ('expr', 11), ('const', 12), ('branch', 0, 26)),
        (('word', 9), ('unop', None, 20), ('ref', 10), ('goto', 3, 25, 26), ('gosub', 6, 25, 26), ('expr', 11), ('const', 12), ('branch', 0, 25, 26)),
        (('mark', 4, 17),),
        (('return', 0, 29), ('goto', 3, 28), ('mark', 4, 30)),
        (('goto', 14),),
        (('return', None, 27),),
        (('word', 15), ('unop', None, 22), ('ref', 16), ('goto', 3, 26), ('gosub', 6, 26), ('expr', 17), ('const', 18), ('branch', 0, 26)),
        (('word', 9), ('unop', None, 20), ('ref', 10), ('goto', 3, 26), ('gosub', 6, 26), ('expr', 11), ('const', 12), ('branch', 0, 26)),
        (('binop', None, 21), ('unop', None, 18), ('expr', 11), ('word', 13), ('ref', 10), ('const', 12), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('binop', None, 21), ('unop', None, 20), ('expr', 11), ('word', 9), ('ref', 10), ('const', 12), ('goto', 3, 25, 26), ('gosub', 6, 25, 26), ('branch', 0, 25, 26)),
        (('binop', None, 21), ('unop', None, 22), ('expr', 17), ('word', 15), ('ref', 16), ('const', 18), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('binop', None, 21), ('unop', None, 20), ('expr', 11), ('word', 9), ('ref', 10), ('const', 12), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('binop', None, 19), ('unop', None, 18), ('expr', 11), ('word', 13), ('ref', 10), ('const', 12), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('mark', 4, 16, 17),),
        (('binop', None, 24), ('unop', None, 18), ('expr', 11), ('word', 13), ('ref', 10), ('const', 12), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('binop', None, 24), ('unop', None, 20), ('expr', 11), ('word', 9), ('ref', 10), ('const', 12), ('goto', 3, 25, 26), ('gosub', 6, 25, 26), ('branch', 0, 25, 26)),
        (('binop', None, 23), ('unop', None, 22), ('expr', 17), ('word', 15), ('ref', 16), ('const', 18), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
        (('binop', None, 24), ('unop', None, 20), ('expr', 11), ('word', 9), ('ref', 10), ('const', 12), ('goto', 3, 26), ('gosub', 6, 26), ('branch', 0, 26)),
    )

    order = {
        'unop': {'int', 'not'},
        'binop': {'<>', 'or', '<=', 'and', '+', '=', '-', '>=', '<', '*', '>', '/', '\\'},
        'const': {'ref', 'word', 'expr'},
        'branch': {'gosub', 'goto'}
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
            owner.gosub_return,
            owner.mark_goto,
            owner.mark_final,
            owner.mark_mark
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
