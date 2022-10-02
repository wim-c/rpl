
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        (('goto', 2, 4), ('final', 1), ('byte_data', None, 0), ('word', 4), ('gosub', 5, 2), ('mark', 0, 1), ('cond', 3, 3)),
        (('const', None, 13), ('command', None, 12), ('mark', 0, 14, 1)),
        (('const', None, 13), ('command', None, 12), ('mark', 0, 5, 14, 1)),
        (('return', 6), ('goto', 7, 4)),
        (('cond', None, 9), ('=', 8), ('<>', 9)),
        (('return', None, 8),),
        (('const', None, 13), ('command', None, 12), ('mark', 0, 7, 14, 1)),
        (('const', None, 13), ('command', None, 12), ('mark', 0, 6, 5, 14, 1)),
        (('cond', 3, 10, 3),),
        (('cond', 3, 11, 3),),
    )

    order = {
        'cond': {'bne', 'beq'},
        'command': {'/', 'mod', 'return', 'or', 'beq', 'print', '@', 'bne', 'xor', '-', 'on', 'dup', '<>', 'int', 'goto', 'str$', 'swap', 'get', 'not', 'req', 'rne', 'input', 'clr', 'drop', '*', 'poke', 'rot', 'peek', 'next', 'pick', '/mod', 'roll', 'gosub', '=', '>=', 'rnd', '<', 'and', 'over', 'new', 'sys', '!', 'fn', '>', 'for', 'stop', '+', '<=', 'chr$'},
        'const': {'expr', 'ref', 'word'},
        'final': {'goto', 'return', 'stop'}
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
