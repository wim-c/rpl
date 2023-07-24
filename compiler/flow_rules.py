
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('mark', 0, 1), ('goto', 5, 4), ('final', 1), ('gosub', 3, 2), ('byte_data', None, 0), ('boolop', 2), ('branch', 4, 3), ('word', 6)),
        (('mark', 0, 14, 1), ('const', None, 13), ('command', None, 12)),
        (('not', 8),),
        (('return', None, 8),),
        (('return', 9), ('goto', 10, 4)),
        (('mark', 0, 5, 14, 1), ('const', None, 13), ('command', None, 12)),
        (('=', 7), ('branch', None, 9)),
        (('not', 8), ('branch', 4, 10, 3)),
        (('branch', None, 11),),
        (('mark', 0, 7, 14, 1), ('const', None, 13), ('command', None, 12)),
        (('mark', 0, 6, 5, 14, 1), ('const', None, 13), ('command', None, 12)),
    )

    order = {
        'branch': {'beq', 'bne'},
        'boolop': {'=', '<', '>'},
        'command': {'on', 'boolop', 'over', '/', 'and', 'not', '>', 'pick', 'fn', '/mod', 'drop', 'mod', 'gosub', 'sys', 'rnd', 'goto', 'rne', 'bne', 'peek', 'dup', 'roll', 'for', 'rot', 'stop', 'return', '=', 'or', 'new', 'next', 'chr$', '*', 'str$', '+', '-', 'clr', 'req', '!', 'xor', 'print', 'beq', 'swap', '@', 'int', '<', 'input', 'get', 'poke'},
        'const': {'word', 'expr', 'ref'},
        'final': {'stop', 'goto', 'return'}
    }

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            owner.push_byte_data,
            owner.push_mark,
            owner.push_gosub,
            owner.push_branch,
            owner.push_goto,
            owner.goto_mark,
            owner.branch_goto_mark,
            owner.branch_return_mark,
            owner.gosub_return,
            owner.word_branch,
            owner.word_eq_branch,
            owner.negate_branch,
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
