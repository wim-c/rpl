
# The Node is the common baseclass of all syntax nodes.
class Node(object):
    def __init__(self, node, value=None):
        super().__init__()
        if isinstance(node, Node):
            self.line = node.line
            self.column = node.column
        else:
            self.line = node.lineno
            self.column = node.lexpos - node.lexer.linepos
        self.value = node.value if value is None else value


# Tokens will not end up in the parse tree.
class Token(Node):
    pass


# Command tokens have no auxiliary parameters.  The value attribute indicates
# the actual command.
class Command(Node):
    ADD = '+'
    AND = 'and'
    BEQ = 'beq'
    BNE = 'bne'
    CONTIF = 'contif'
    CALL = '&'
    CHR = 'chr$'
    CLR = 'clr'
    DIV = '/'
    DROP = '.'
    DUP = '#'
    EQ = '='
    FETCH = '@'
    FN = 'fn'
    FOR = 'for'
    GE = '>='
    GET = 'get'
    GOTO = 'goto'
    GT = '>'
    INPUT = 'input'
    INT = 'int'
    LE = '<='
    LT = '<'
    MOD = '\\'
    MUL = '*'
    NE = '<>'
    NEW = 'new'
    NEXT = 'next'
    NOT = 'not'
    OR = 'or'
    OVER = ';'
    PEEK = 'peek'
    PICK = '^'
    POKE = 'poke'
    PRINT = 'print'
    RETURN = 'return'
    RND = 'rnd'
    ROLL = '$'
    STOP = 'stop'
    STORE = '!'
    STR = 'str$'
    SUB = '-'
    SWAP = '%'
    SYS = 'sys'

    def __init__(self, token, value=None):
        super().__init__(token, value)
        self.type = self.value.lower()


class Integer(Node):
    type = 'word'

    def __init__(self, token, value=None):
        # Normalize value to signed word.
        if value is not None:
            value = value & 0xffff
            if value >= 0x8000:
                value -= 0x10000

        super().__init__(token, value)


class Symbol(Node):
    type = 'symbol'


class Label(Node):
    type = 'label'


class Chars(Node):
    type = 'chars'


class String(Node):
    type = 'string'


class Float(Node):
    type = 'float'


class If(Node):
    type = 'if'


class Bytes(Node):
    type = 'bytes'


class Macro(Node):
    type = 'macro'


class Proc(Node):
    type = 'proc'


class Words(Node):
    type = 'words'
