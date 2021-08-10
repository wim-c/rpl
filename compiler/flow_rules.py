
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('mark', 0, 0), ('goto', 1, 3), ('final', 2), ('cond', 3, 2), ('word', 4), ('gosub', 5, 1)),
        (('command', None, 10), ('mark', 0, 4, 0), ('const', None, 11)),
        (('command', None, 10), ('const', None, 11)),
        (('goto', 6, 3),),
        (('<>', 7), ('cond', None, 7), ('=', 8)),
        (('return', None, 6),),
        (('command', None, 10), ('mark', 0, 5, 4, 0), ('const', None, 11)),
        (('cond', 3, 9, 2),),
        (('cond', 3, 8, 2),),
    )

    order = {
        'cond': {'bne', 'beq'},
        'final': {'return', 'goto', 'stop'},
        'command': {'@', '!', 'clr', 'goto', '\\', '+', '=', '>', 'not', '$', 'rnd', 'int', 'bne', '*', ';', '%', 'new', 'get', 'sys', 'chr$', 'next', 'on', 'peek', '<>', '/', '.', '-', 'poke', '<=', 'print', '<', 'and', '#', 'gosub', 'fn', '>=', 'beq', 'for', 'input', 'return', 'str$', '^', 'stop', 'or'},
        'const': {'expr', 'word', 'ref'}
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
            owner.final_const
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
