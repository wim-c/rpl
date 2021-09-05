
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('THEN', None, 1), ('if', None, 8), ('define_proc', None, 7), ('expr', 1), ('define_macro', None, 6), ('symbol', None, 15), ('program', None, 13), ('ref', 4), ('word', 6), ('const', 3), ('bytes', None, 2), ('END', None, 0), ('mark', 5), ('data', None, 4), ('define_data', None, 5), ('statements', None, 14), ('words', None, 16), ('label', None, 9), ('proc_body', None, 12), ('proc', None, 11), ('macro', None, 10), ('contif', None, 3), ('compare', 2)),
        (('expr', 12), ('unop', None, 21), ('ref', 14), ('word', 15), ('const', 13), ('branch', 0, 25)),
        (('not', None, 29),),
        (('expr', 7), ('unop', None, 19), ('ref', 9), ('word', 11), ('const', 8), ('branch', 0, 25)),
        (('expr', 7), ('unop', None, 19), ('ref', 9), ('word', 11), ('const', 8), ('branch', 0, 24, 25)),
        (('stop', 0, 27), ('mark', 5, 28), ('return', 0, 27), ('goto', 0, 26)),
        (('expr', 7), ('unop', None, 17), ('ref', 9), ('word', 10), ('const', 8), ('branch', 0, 25)),
        (('word', 15), ('branch', 0, 25), ('expr', 12), ('unop', None, 21), ('ref', 14), ('const', 13), ('binop', None, 20)),
        (('word', 11), ('branch', 0, 25), ('expr', 7), ('unop', None, 19), ('ref', 9), ('const', 8), ('binop', None, 20)),
        (('word', 11), ('branch', 0, 24, 25), ('expr', 7), ('unop', None, 19), ('ref', 9), ('const', 8), ('binop', None, 20)),
        (('word', 10), ('branch', 0, 25), ('expr', 7), ('unop', None, 17), ('ref', 9), ('const', 8), ('binop', None, 18)),
        (('word', 10), ('branch', 0, 25), ('expr', 7), ('unop', None, 17), ('ref', 9), ('const', 8), ('binop', None, 20)),
        (('word', 15), ('branch', 0, 25), ('expr', 12), ('unop', None, 21), ('ref', 14), ('const', 13), ('binop', None, 22)),
        (('word', 11), ('branch', 0, 25), ('expr', 7), ('unop', None, 19), ('ref', 9), ('const', 8), ('binop', None, 23)),
        (('word', 11), ('branch', 0, 24, 25), ('expr', 7), ('unop', None, 19), ('ref', 9), ('const', 8), ('binop', None, 23)),
        (('word', 10), ('branch', 0, 25), ('expr', 7), ('unop', None, 17), ('ref', 9), ('const', 8), ('binop', None, 23)),
    )

    order = {
        'unop': {'not', 'int'},
        'binop': {'<=', '=', '<>', '\\', '>', '<', '>=', '*', '/', 'or', '+', 'and', '-', 'compare'},
        'const': {'expr', 'ref', 'word'},
        'branch': {'gosub', 'goto'},
        'compare': {'<=', '<>', '>', '<', '>=', '='}
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
