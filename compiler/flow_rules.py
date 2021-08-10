
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('gosub', 1, 1), ('cond', 2, 2), ('goto', 5, 3), ('final', 3), ('mark', 0, 0), ('word', 4)),
        (('return', None, 6),),
        (('goto', 8, 3),),
        (('command', None, 10), ('const', None, 11), ('mark', 0, 12, 0)),
        (('cond', None, 7), ('=', 6), ('<>', 7)),
        (('command', None, 10), ('const', None, 11), ('mark', 0, 4, 12, 0)),
        (('cond', 2, 8, 2),),
        (('cond', 2, 9, 2),),
        (('command', None, 10), ('const', None, 11), ('mark', 0, 5, 4, 12, 0)),
    )

    order = {
        'cond': {'beq', 'bne'},
        'final': {'return', 'goto', 'stop'},
        'command': {'fn', 'gosub', '<=', 'stop', 'bne', '.', 'or', 'int', '%', 'goto', ';', '+', '/', 'str$', 'next', 'return', 'peek', 'get', '<', '-', '*', 'new', 'on', 'not', '=', '!', '#', 'input', '$', 'and', 'chr$', 'print', 'sys', '<>', '>', 'poke', 'for', 'rnd', '@', 'beq', '>=', 'clr', '\\', '^'},
        'const': {'ref', 'expr', 'word'}
    }

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            owner.push_mark,
            owner.push_gosub,
            owner.push_cond,
            owner.push_goto,
            owner.goto_mark,
            owner.cond_goto_mark,
            owner.gosub_return,
            owner.word_cond,
            owner.word_eq_cond,
            owner.word_neq_cond,
            owner.final_command,
            owner.final_const,
            owner.final_mark
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
