
import re


# The Token is the common baseclass of all syntax nodes.
class Token(object):
    def __init__(self, token, value=None):
        super().__init__()
        if isinstance(token, Token):
            self.line = token.line
            self.column = token.column
        else:
            self.line = token.lineno
            self.column = token.lexpos - token.lexer.linepos
        self.value = token.value if value is None else value


# Command tokens have no auxiliary parameters.  The value attribute indicates
# the actual command.
class Command(Token):
    ADD = '+'
    AND = 'and'
    BEQ = 'beq'
    BNE = 'bne'
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

    unary = (INT, NOT)
    binary = (ADD, AND, DIV, EQ, GE, GT, LE, LT, MOD, MUL, NE, OR, SUB, SWAP)

    def __init__(self, token, value=None):
        super().__init__(token, value)
        self.address = None

    def __str__(self):
        return self.value if self.address is None else f'{self.value} {self.address}'


# The Constant token is an abstract base class for all syntax nodes that
# evaluate to a constant word at compile time.
class Constant(Token):
    pass


# A Target token represents a syntax node to which the compiler assign an
# address.  Each target is a constant since its address is knonw  at compile
# time.
class Target(Constant):
    def __init__(self, token, value=None):
        super().__init__(token, value)
        self.address = None


# A ConstantExpression is a constant that depends on parameters that are not
# yet known but will be eventually determined at compile time.  This can be
# labels or  addresses of implicit data items.  The expression is kept as a
# sequence of statements that can be evaluated later.
class ConstantExpression(Constant):
    pass


class Integer(Constant):
    def __init__(self, token, value=None):
        super().__init__(token, int(token.value) if value is None else value)
        self.value = self.value & 0xffff
        if self.value >= 0x8000:
            self.value -= 0x10000

    def __str__(self):
        return f'{self.value}'


class Symbol(Token):
    pass


class StringConstant(Constant):
    def __init__(self, token, value=None):
        if value is None:
            def tochar(m):
                return chr(int(m.group(1)) & 0xff)
            value = re.sub(r'\\(\d{1,3})', tochar, token.value[1:-1])
        super().__init__(token, value)


class Chars(StringConstant, Target):
    pass


class Float(Target):
    def __init__(self, token, value=None):
        super().__init__(token, float(token.value) if value is None else value)


class String(StringConstant, Target):
    pass


class If(Token):
    def __init__(self, token, value, then_statements=None):
        super().__init__(token, value)
        self.then_statements = then_statements


class Label(Target):
    pass


# A block represents a syntax node that has statements as its value and an
# optional label.
class Block(Token):
    def __init__(self, token, value):
        super().__init__(token, value)
        statements = self.value.statements
        if len(statements) > 0 and isinstance(statements[0], Label):
            self.label = statements[0].value
        else:
            self.label = None


class Bytes(Target, Block):
    pass


class Macro(Block):
    pass


class Proc(Target, Block):
    pass


class Words(Target, Block):
    pass


# The value of a Reference syntax node is a target.
class Reference(Constant):
    pass


class Scope(object):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.chars = {}
        self.float = {}
        self.string = {}

    def error(self, item, msg):
        self.errors.append(f'Line {item.line} column {item.column}: {msg}')

    def error_redefined_label(self, name, second_item, first_item):
        self.error(second_item, f'Label \'{name}\' already defined at line {first_item.line} column {first_item.columne}')

    def statements(self):
        return Statements(self)

    def intern(self, literal):
        if isinstance(literal, Chars):
            interned = self.chars
        elif isinstance(literal, Float):
            interned = self.float
        elif isinstance(literal, String):
            interned = self.string

        if literal.value in interned:
            return interned[literal.value]

        interned[literal.value] = literal
        return literal


class Statements(object):
    terminal_commands = (
        Command.GOTO,
        Command.RETURN,
        Command.STOP
    )

    def __init__(self, scope):
        super().__init__()
        self.scope = scope
        self.statements = []
        self.labels = {}
        self.bytes = []
        self.proc = []
        self.words = []
        self._reachable_code = True

    def _add_label(self, name, item):
        if name in self.labels:
            self.scope.error_redefined_label(name, item, self.labels[name])
        else:
            self.labels[name] = item

    def append(self, statement):
        print(f'append {statement}')
        if isinstance(statement, Label):
            self._reachable_code = True
        elif not self._reachable_code:
            return
        elif isinstance(statement, Command):
            self._reachable_code = statement.value not in self.terminal_commands
        self.statements.append(statement)

    def block(self, block):
        if block.label is not None:
            # Labeled blocks are added to the symbol table and an implicit stop
            # command is inserted in the code.
            self._add_label(block.label, block)
            self.append(Command(block, Command.STOP))
        elif isinstance(block, Target):
            # A reference is inserted if the unlabeled block is a target.  The
            # block itself is added to a list of targets to be emitted by the
            # compiler later.
            self.append(Reference(block, block))
        else:
            # Otherwise the unlabeled block is a local scope and it is added to
            # the code directly.
            self.append(block)

        # Add target blocks by their type to a list of blocks to be emitted
        # later by the compiler.
        if isinstance(block, Target):
            if isinstance(block, Bytes):
                blocks = self.bytes
            elif isinstance(block, Proc):
                blocks = self.proc
            elif isinstance(block, Words):
                blocks = self.words
            blocks.append(block)

    def label(self, label):
        self._add_label(label.value, label)
        self.append(label)

    def literal(self, literal):
        interned = self.scope.intern(literal)
        self.append(Reference(literal, interned))


