import math

# Abstract base class of all objects that can appear in a program.  The type of
# the object (a string) is used in reduction rules for the optimizer.  See the
# file rules.txt for all reduction rules.  A node instance can copy source file
# location data either from a PLY token or from another Node.
class Node:
    def __init__(self):
        super().__init__()
        self.line = None
        self.column = None

    # Return the type for this node that is used in reduction rules.
    def get_type(self):
        return self.type

    # Override to move symbol definitions into an enclosing Statements node.
    # This method is called when a Node is (indirectly) added to a Statements
    # node.
    def move_symbols(self, statements):
        pass

    # Set the location data from a PLY token.
    def from_token(self, t):
        self.line = t.lineno
        self.column = t.lexpos - t.lexer.linepos
        return self

    # Copy the location data from another Node.
    def from_node(self, n):
        self.line = n.line
        self.column = n.column
        return self


# Concrete node types in alphabetical order.

class Bytes(Node):
    type = 'bytes'

    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def move_symbols(self, statements):
        self.statements.move_symbols(statements)


class Chars(Node):
    type = 'chars'

    def __init__(self, value):
        super().__init__()
        self.value = value


# Command tokens have no auxiliary parameters.  The value attribute indicates
# the actual command.
class Command(Node):
    ADD = '+'
    AND = 'and'
    BEQ = 'beq'
    BNE = 'bne'
    CONTIF = 'contif'
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
    GOSUB = 'gosub'
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
    ON = 'on'
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

    def __init__(self, type):
        super().__init__()
        self.type = type


# Suequence of data blocks that together form a single block of data
# bytes in a compiled program.
class Data(Node):
    type = 'data'

    def __init__(self, blocks):
        super().__init__()
        self.blocks = blocks

    # A data node does not define a new scope.  Move the symbols of all
    # contained word and byte blocks to an enclosing Statements node.
    def move_symbols(self, statements):
        for block in self.blocks:
            block.move_symbols(statements)


class Float(Node):
    type = 'float'

    def __init__(self, value):
        super().__init__()
        self.value = value

    def set_data(self):
        if number >= 0:
            # Mask out sign bit.
            mask = 0x7f
        else:
            # Leave sign bit at 1 and make sure that the mantissa is positive.
            mask = 0xff
            number = -number

        if number < pow(2.0, -129):
            # Map numbers below smallest representable number to zero.
            data = bytes(5)
        else:
            # Determine exponent and rounded mantissa.
            e = math.floor(math.log2(number)) + 1
            m = math.trunc(number*pow(2.0, 32 - e) + 0.5)

            # Correct possible mantissa overflow due to rounding.
            if m == 0x1_0000_0000:
                e += 1
                m = 0x8000_0000

            if e > 127:
                # Replace number above maximum representable number by this
                # maximum.
                data = bytes([0xff, 0xff & mask, 0xff, 0xff, 0xff])
            else:
                # Get the four bytes of the mantissa.  Note that the sign bit
                # (bit 7 of data[0]) will always be 1.
                data = m.to_bytes(4, 'big')

                # Create the final five byte floating point number.  Center the
                # exponent around 128 and mask out the sign bit for positive
                # numbers.
                data = bytes([128 + e, data[0] & mask, data[1], data[2], data[3]])

        self.data = data


class If(Node):
    type = 'if'
    
    def __init__(self, blocks):
        super().__init__()
        self.blocks = blocks

    def move_symbols(self, statements):
        for block in self.blocks:
            block.move_symbols(statements)


class Integer(Node):
    type = 'word'

    def __init__(self, value):
        super().__init__()

        # Normalize value to signed word.
        value = value & 0xffff
        if value >= 0x8000:
            value -= 0x10000

        self.value = value


class Label(Node):
    type = 'label'

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def move_symbols(self, statements):
        statements.add_label(self)


class Let(Node):
    type = 'let'

    def __init__(self, symbol, definition):
        super().__init__()
        self.symbol = symbol
        self.definition = definition

    def move_symbols(self, statements):
        statements.add_definition(self)
        self.definition.move_symbols(statements)


class Macro(Node):
    type = 'macro'

    def __init__(self, statements):
        super().__init__()
        self.statements = statements


class Proc(Node):
    type = 'proc'

    def __init__(self, statements):
        super().__init__()
        self.statements = statements


# A Program represents the top level statements of an rpl program.  A Program
# instance is the top node in a parse tree.
class Program(Node):
    type = 'program'

    def __init__(self, statements):
        super().__init__()
        self.statements = statements


# Sequence of statements that appear in a program, data definition (words or
# bytes), procedure, or macro.  Symbol definitions introduced by labels and let
# statements are maintained separately for easy access during compilation.
class Statements(Node):
    type = 'statements'

    def __init__(self):
        super().__init__()
        self.labels = []
        self.definitions = []
        self.statements = []

    def append(self, statement):
        self.statements.append(statement)
        statement.move_symbols(self)

    def extend(self, statements):
        self.statements.extend(statements.statements)
        statements.move_symbols(self)

    def add_label(self, label):
        self.labels.append(label)

    def add_definition(self, definition):
        self.definitions.append(definition)

    def add_statements(self, statements):
        self.labels.extend(statements.labels)
        self.definitions.extend(statements.definitions)

    def move_symbols(self, statements):
        statements.add_statements(self)
        self.labels.clear()
        self.definitions.clear()


class String(Node):
    type = 'string'

    def __init__(self, value):
        self.value = value


class Symbol(Node):
    type = 'symbol'

    def __init__(self, symbol):
        self.symbol = symbol


class Token(Node):
    def __init__(self, type):
        super().__init__()
        self.type = type


class Words(Node):
    type = 'words'

    def __init__(self, statements):
        self.statements = statements

    def move_symbols(self, statements):
        self.statements.move_symbols(statements)
