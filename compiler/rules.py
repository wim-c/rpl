
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('literal', 0, 8), ('ref', 2), ('END', None, 0), ('THEN', None, 1), ('bytes', None, 2), ('word', 3), ('symbol', None, 13), ('data', None, 4), ('statements', None, 12), ('proc', None, 10), ('if', None, 5), ('expr', 5), ('const', 4), ('contif', None, 3), ('label', None, 6), ('compare', 1), ('macro', None, 9), ('let', 6, 7), ('mark', 7), ('program', None, 11)),
        (('not', None, 29),),
        (('ref', 8), ('word', 12), ('unop', None, 19), ('expr', 11), ('const', 10), ('branch', 0, 24, 25)),
        (('ref', 8), ('word', 9), ('unop', None, 17), ('expr', 11), ('const', 10), ('branch', 0, 25)),
        (('ref', 8), ('word', 12), ('unop', None, 19), ('expr', 11), ('const', 10), ('branch', 0, 25)),
        (('ref', 13), ('word', 14), ('unop', None, 21), ('expr', 16), ('const', 15), ('branch', 0, 25)),
        (('data', None, 14), ('proc', None, 16), ('macro', None, 15)),
        (('stop', 0, 27), ('goto', 0, 26), ('return', 0, 27), ('mark', 7, 28)),
        (('ref', 8), ('unop', None, 19), ('expr', 11), ('word', 12), ('const', 10), ('branch', 0, 24, 25), ('binop', None, 20)),
        (('ref', 8), ('unop', None, 17), ('expr', 11), ('word', 9), ('const', 10), ('branch', 0, 25), ('binop', None, 18)),
        (('ref', 8), ('unop', None, 19), ('expr', 11), ('word', 12), ('const', 10), ('branch', 0, 25), ('binop', None, 20)),
        (('ref', 13), ('unop', None, 21), ('expr', 16), ('word', 14), ('const', 15), ('branch', 0, 25), ('binop', None, 20)),
        (('ref', 8), ('unop', None, 17), ('expr', 11), ('word', 9), ('const', 10), ('branch', 0, 25), ('binop', None, 20)),
        (('ref', 8), ('unop', None, 19), ('expr', 11), ('word', 12), ('const', 10), ('branch', 0, 24, 25), ('binop', None, 23)),
        (('ref', 8), ('unop', None, 17), ('expr', 11), ('word', 9), ('const', 10), ('branch', 0, 25), ('binop', None, 23)),
        (('ref', 8), ('unop', None, 19), ('expr', 11), ('word', 12), ('const', 10), ('branch', 0, 25), ('binop', None, 23)),
        (('ref', 13), ('unop', None, 21), ('expr', 16), ('word', 14), ('const', 15), ('branch', 0, 25), ('binop', None, 22)),
    )

    order = {
        'literal': {'chars', 'string', 'float'},
        'unop': {'not', 'int'},
        'binop': {'<=', '=', '<>', '*', '\\', '<', '>=', 'and', 'or', '/', 'compare', '>', '+', '-'},
        'const': {'expr', 'word', 'ref'},
        'branch': {'gosub', 'goto'},
        'compare': {'<=', '=', '<>', '<', '>=', '>'}
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
