
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('mark', 0, 0), ('gosub', 0, 1), ('goto', 2, 3), ('final', 1), ('branch', 0, 2)),
        (('command', None, 5), ('const', None, 6)),
        (('mark', 0, 4, 0), ('command', None, 5), ('const', None, 6)),
    )

    order = {
        'branch': {'bne', 'beq'},
        'final': {'goto', 'stop', 'return'},
        'command': {'int', 'next', 'or', 'not', 'rnd', 'str$', '-', 'poke', '@', '\\', 'stop', '<>', 'sys', '#', '$', '*', 'return', 'chr$', 'and', 'fn', '%', '>=', 'new', 'input', '^', '!', 'for', 'clr', '<=', 'print', 'beq', 'goto', '+', 'get', 'gosub', 'peek', '.', ';', '/', 'on', '>', '<', 'bne', '='},
        'const': {'ref', 'word', 'expr'}
    }

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            owner.push_mark,
            owner.push_gosub,
            owner.push_branch,
            owner.push_goto,
            owner.goto_mark,
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
