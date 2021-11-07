
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('word', 2), ('cond', 1, 2), ('mark', 0, 0), ('goto', 4, 3), ('final', 3), ('gosub', 5, 1)),
        (('return', 8), ('goto', 9, 3)),
        (('cond', None, 8), ('=', 6), ('<>', 7)),
        (('command', None, 11), ('mark', 0, 13, 0), ('const', None, 12)),
        (('command', None, 11), ('mark', 0, 4, 13, 0), ('const', None, 12)),
        (('return', None, 7),),
        (('cond', 1, 9, 2),),
        (('cond', 1, 10, 2),),
        (('command', None, 11), ('mark', 0, 6, 13, 0), ('const', None, 12)),
        (('command', None, 11), ('mark', 0, 5, 4, 13, 0), ('const', None, 12)),
    )

    order = {
        'cond': {'bne', 'beq'},
        'command': {'#', '=', '.', 'req', '<>', 'sys', '<=', 'input', 'rne', '!', 'and', 'or', '^', 'new', 'beq', 'clr', 'poke', '<', 'gosub', '/', '%', 'str$', 'bne', 'stop', ';', 'chr$', '>', 'for', '@', 'next', '$', 'fn', 'return', 'int', 'goto', '\\', 'print', 'on', 'not', 'peek', '>=', '-', '*', 'get', 'rnd', '+'},
        'const': {'word', 'ref', 'expr'},
        'final': {'stop', 'goto', 'return'}
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
            owner.cond_return_mark,
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
