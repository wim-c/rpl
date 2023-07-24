
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('ref', 1), ('symbol', None, 13), ('mark', 2), ('bytes', None, 2), ('if', None, 5), ('let', 3, 7), ('program', None, 11), ('literal', 0, 8), ('data', None, 4), ('statements', None, 12), ('THEN', None, 1), ('pseudo_op', None, 14), ('expr', 4), ('word', 5), ('label', None, 6), ('macro', None, 9), ('proc', None, 10), ('END', None, 0), ('contif', None, 3), ('const', 6)),
        (('ref', 7), ('dup', None, 30), ('expr', 8), ('word', 11), ('branch', 0, 25, 26), ('unop', None, 20), ('const', 10)),
        (('return', 0, 28), ('mark', 2, 29), ('goto', 0, 27), ('stop', 0, 28)),
        (('data', None, 15), ('macro', None, 16), ('proc', None, 17)),
        (('ref', 12), ('dup', None, 30), ('expr', 13), ('word', 14), ('branch', 0, 26), ('unop', None, 22), ('const', 15)),
        (('ref', 7), ('dup', None, 30), ('expr', 8), ('word', 9), ('branch', 0, 26), ('unop', None, 18), ('const', 10)),
        (('ref', 7), ('dup', None, 30), ('expr', 8), ('word', 11), ('branch', 0, 26), ('unop', None, 20), ('const', 10)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 25, 26), ('over', None, 31), ('word', 11), ('const', 10), ('binop', None, 21), ('unop', None, 20)),
        (('ref', 12), ('dup', None, 30), ('swap', None, 32), ('expr', 13), ('branch', 0, 26), ('over', None, 31), ('word', 14), ('const', 15), ('binop', None, 21), ('unop', None, 22)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 26), ('over', None, 31), ('word', 9), ('const', 10), ('binop', None, 19), ('unop', None, 18)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 26), ('over', None, 31), ('word', 11), ('const', 10), ('binop', None, 21), ('unop', None, 20)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 26), ('over', None, 31), ('word', 9), ('const', 10), ('binop', None, 21), ('unop', None, 18)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 25, 26), ('over', None, 31), ('word', 11), ('const', 10), ('binop', None, 24), ('unop', None, 20)),
        (('ref', 12), ('dup', None, 30), ('swap', None, 32), ('expr', 13), ('branch', 0, 26), ('over', None, 31), ('word', 14), ('const', 15), ('binop', None, 23), ('unop', None, 22)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 26), ('over', None, 31), ('word', 9), ('const', 10), ('binop', None, 24), ('unop', None, 18)),
        (('ref', 7), ('dup', None, 30), ('swap', None, 32), ('expr', 8), ('branch', 0, 26), ('over', None, 31), ('word', 11), ('const', 10), ('binop', None, 24), ('unop', None, 20)),
    )

    order = {
        'literal': {'chars', 'string', 'float'},
        'pseudo_op': {'>=', '<>', '<='},
        'unop': {'not', 'int'},
        'binop': {'or', '-', '<', '>', 'and', 'mod', '=', 'xor', '+', '/', '*'},
        'const': {'ref', 'expr', 'word'},
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
            owner.push_if,
            owner.push_label,
            owner.push_let,
            owner.push_literal,
            owner.push_macro,
            owner.push_proc,
            owner.push_program,
            owner.push_statements,
            owner.push_symbol,
            owner.push_pseudo_op,
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
