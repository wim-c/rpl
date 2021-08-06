import math
import ops

# Normalize an integral value to the signed word range.
def to_word(value):
    value = value & 0xffff
    if value >= 0x8000:
        value -= 0x10000
    return value


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

    # Create a mark for this node as entry in a scope's symbol table.
    def mark(self):
        return Mark(self)

    # Get a node value from a marked object in a scope's symbol table.
    def resolve_mark(self, mark):
        return Reference(mark)

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

    # Assign address to this node's code and return the next address.
    def assign_address(self, address):
        # Generate no code by default.
        return address

    # Assign address to this node's code and return the next address based on
    # the encoding of the mark (relative or absolute).
    def assign_offset_address(self, address, target):
        if (target <= address and address - target <= 0xff) or \
           (target >= address + 2 and target - address - 2 <= 0xff):
            # Relative encoding of target.
            return address + 2
        else:
            # Absolute encoding of target.
            return address + 3

    # Assign address to this node's code and return the next address based on
    # the encoding of a signed word value.
    def assign_value_address(self, address, value):
        if -32 <= value and value < 32:
            return address + 1
        elif -8192 <= value and value < 8192:
            return address + 2
        else:
            return address + 3

    # Assign address to this node's data inside a DataBlock block.
    def assign_word_address(self, address):
        # Assume word size.
        return address + 2

    # Assign address to this node's data inside a ByteData node.
    def assign_byte_address(self, address):
        # Assume byte size.
        return address + 1

    # Evaluate this node or return None if the node cannot be evaluated (yet).
    def eval(self):
        return None

    # Push this node on the provided stack as an action to evaluate a compile
    # time expressions.  Either pushes a word to the stack or manipulates the
    # current stack content.  Returns True if the node was pushed.
    def push_to(self, stack):
        value = self.eval()
        if value is not None:
            stack.append(value)
            return True


# Concrete node types in alphabetical order.

class ByteData(Node):
    type = 'byte_data'

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def assign_word_address(self, address):
        for node in self.nodes:
            address = node.assign_byte_address(address)
        return address


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

    def assign_word_address(self, address):
        return address + len(self.value)


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
    GEQ = '>='
    GET = 'get'
    GOSUB = 'gosub'
    GOTO = 'goto'
    GT = '>'
    INPUT = 'input'
    INT = 'int'
    LEQ = '<='
    LT = '<'
    MOD = '\\'
    MUL = '*'
    NEQ = '<>'
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

    def __init__(self, type, *, command=None, mark=None, const=None):
        super().__init__()
        self.type = type
        if command is None:
            self.mark = mark
            self.const = const
        else:
            self.mark = command.mark if mark is None else mark
            self.const = command.const if const is None else const

    def get_op(self):
        return self.ops[self.type]

    def has_data(self):
        return self.mark is not None or self.const is not None

    def assign_address(self, address):
        if self.type not in self.branches:
            return address + 1
        elif self.mark is not None and self.mark.address is not None:
            return self.assign_offset_address(address, self.mark.address)
        elif self.const is not None and (value := self.const.eval()) is not None:
            return self.assign_offset_address(address, value)
        else:
            return address + 3

    def push_to(self, stack):
        op = self.ops.get(self.type)
        if op is None:
            return
        elif op.arity == 1:
            stack[-1] = to_word(op(stack[-1]))
        else:
            y = stack.pop()
            stack[-1] = to_word(op(stack[-1], y))
        return True

Command.branches = {
    Command.BEQ,
    Command.BNE,
    Command.GOSUB,
    Command.GOTO
}

Command.ops = {
    Command.ADD: ops.binop_add,
    Command.AND: ops.binop_and,
    Command.DIV: ops.binop_div,
    Command.EQ: ops.binop_eq,
    Command.GEQ: ops.binop_geq,
    Command.GT: ops.binop_gt,
    Command.INT: ops.unop_int,
    Command.LEQ: ops.binop_leq,
    Command.LT: ops.binop_lt,
    Command.MOD: ops.binop_mod,
    Command.MUL: ops.binop_mul,
    Command.NEQ: ops.binop_neq,
    Command.NOT: ops.unop_not,
    Command.OR: ops.binop_or,
    Command.SUB: ops.binop_sub
}


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


class Expression(Node):
    type = 'expr'

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def append(self, node):
        self.nodes.append(node)

    def extend(self, nodes):
        self.nodes.extend(nodes)

    def assign_address(self, address):
        value = self.eval()
        if value is None:
            return address + 3
        else:
            return self.assign_value_address(address, value)

    def eval(self):
        stack = []
        for node in self.nodes:
            if not node.push_to(stack):
                return
        return stack[0]


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

    def assign_word_address(self, address):
        return address + 5


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
        self.value = to_word(value)

    def assign_address(self, address):
        return self.assign_value_address(address, self.value)

    def eval(self):
        return self.value


class Label(Node):
    type = 'label'

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def move_symbols(self, statements):
        statements.add_label(self)


class Let(Node):
    def __init__(self, symbol, definition):
        super().__init__()
        self.symbol = symbol
        self.definition = definition
        self.type = f'define_{definition.get_type()}'

    def move_symbols(self, statements):
        statements.add_definition(self)
        self.definition.move_symbols(statements)


class Macro(Node):
    type = 'macro'

    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def resolve_mark(self, mark):
        return Macro(self.statements)


class Mark(Node):
    type = 'mark'

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.address = None
        self.marked = None

    def resolve(self):
        return self.node.resolve_mark(self)

    def assign_address(self, address):
        self.address = address
        return address

    def assign_word_address(self, address):
        return self.assign_address(address)

    def assign_byte_address(self, address):
        return self.assign_address(address)


class Preamble(Node):
    type = 'preamble'

    def assign_address(self, address):
        return address + 3


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


# A Reference is a node type that encodes a reference to a Mark node.  A symbol
# node results in such a Reference node after the symbol is resolved in the
# current scope.
class Reference(Node):
    type = 'ref'

    def __init__(self, mark):
        self.mark = mark

    def assign_address(self, address):
        if self.mark.address is None:
            # Assume  encoding with largest next address.
            return address + 3
        else:
            return self.assign_offset_address(address, self.mark.address)

    def eval(self):
        return self.mark.address


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

    def assign_word_address(self, address):
        return address + len(self.value) + 1


class Symbol(Node):
    type = 'symbol'

    def __init__(self, name):
        self.name = name


class Token(Node):
    COLON = ':'
    CONT = 'CONT'
    DATA = 'DATA'
    DEF = 'DEF'
    END = 'END'
    IF = 'IF'
    LBRACKET = '['
    LET = 'LET'
    LPAREN = '('
    RBRACKET = ']'
    RPAREN = ')'
    THEN = 'THEN'

    def __init__(self, type):
        super().__init__()
        self.type = type


class Words(Node):
    type = 'words'

    def __init__(self, statements):
        self.statements = statements

    def move_symbols(self, statements):
        self.statements.move_symbols(statements)
