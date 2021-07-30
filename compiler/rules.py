
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('symbol', None, 14), ('macro', None, 10), ('data', None, 4), ('THEN', None, 1), ('program', None, 12), ('END', None, 0), ('proc', None, 11), ('define_macro', None, 6), ('statements', None, 13), ('define_data', None, 5), ('if', None, 8), ('contif', None, 3), ('label', None, 9), ('define_proc', None, 7), ('words', None, 15), ('bytes', None, 2)),
    )

    order = {
        
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
            owner.push_words
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
