import math
import ops
import re

# Normalize an integral value to the signed word range.
def to_word(value):
    value = value & 0xffff
    if value >= 0x8000:
        value -= 0x10000
    return value


# Escape a string
def escape_string(value):
    def encode(match):
        asc, digit = ord(match[1]), match[2]
        if digit == '':
            return f'\\{asc}'
        else:
            return f'\\{asc:03d}{digit}'

    return re.sub(r'([\x00-\x1f\x80-\x9f])(\d?)', encode, value)


# Abstract base class of all objects that can appear in a program.  The type of
# the object (a string) is used in reduction rules for the optimizer.  See the
# file rules.txt for all reduction rules.  A node instance can copy source file
# location data either from a PLY token or from another Node.
class Node:
    # Create a unique mark id for a specific node type.
    @classmethod
    def get_next_mark_id(cls):
        cls.mark_id += 1
        return cls.mark_id

    # Create a unique mark name for a specific node type.
    def make_mark_name(self):
        return f'{self.get_type()}.{self.get_next_mark_id()}'

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
    def mark(self, name=None):
        return Mark(self, name).from_node(self)

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
        delta = target - address
        if (delta <= 0 and delta >= -0xff) or \
                (delta >= 2 and delta <= 0x101):
            # Relative encoding of target.
            return address + 2
        else:
            # Absolute encoding of target.
            return address + 3

    # Assign address to this node's code and return the next address based on
    # the encoding of a signed word value.
    def assign_value_address(self, address, value):
        if -0x20 <= value and value < 0x20:
            return address + 1
        elif -0x4000 <= value and value < 0x4000:
            return address + 2
        else:
            return self.assign_offset_address(address, value % 0x10000)

    # Assign address to this node's data inside a DataBlock block.
    def assign_word_address(self, address):
        # Assume word size.
        return address + 2

    # Assign address to this node's data inside a ByteData node.
    def assign_byte_address(self, address):
        # Assume byte size.
        return address + 1

    # Indicates that this node is visited in the program.  Do not visit
    # referenced marks directly.  Instead, add referencesd marks to the
    # marks_to_visit set.  Return True if the node after this one should also
    # be set as visited (if present).
    def set_visited(self, marks_to_visit):
        # Set next node visited by default.
        return True

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

    def emit_offset(self, code, address, target, formatter):
        delta = target - address
        if delta <= 0 and delta >= -0xff:
            return formatter.emit(address, bytes([code + 2, -delta]), self)
        elif delta >= 2 and delta <= 0x101:
            return formatter.emit(address, bytes([code + 3, delta - 2]), self)
        else:
            hi, lo = (target >> 8) & 0xff, target & 0xff
            return formatter.emit(address, bytes([code + 1, hi, lo]), self)

    def emit_value(self, address, formatter):
        value = self.eval()
        if -0x20 <= value and value < 0x20:
            return formatter.emit(address, bytes([(value & 0x3f) | 0x80]), self)
        elif -0x4000 <= value and value < 0x4000:
            hi, lo = (value >> 8) & 0x7f, value & 0xff
            return formatter.emit(address, bytes([hi, lo]), self)
        else:
            return self.emit_offset(0xbf, address, value % 0x10000, formatter)

    def emit_word_value(self, address, formatter):
        value = self.eval()
        hi, lo = (value >> 8) & 0xff, value & 0xff
        return formatter.emit(address, bytes([lo, hi]), self)

    def emit_byte_value(self, address, formatter):
        value = self.eval()
        return formatter.emit(address, bytes([value & 0xff]), self)


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

    def set_visited(self, marks_to_visit):
        for node in self.nodes:
            node.set_visited(marks_to_visit)
        return True

    def emit_word(self, address, formatter):
        for node in self.nodes:
            address = node.emit_byte(address, formatter)
        return address


class Bytes(Node):
    type = 'bytes'
    mark_id = 0

    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def move_symbols(self, statements):
        self.statements.move_symbols(statements)


class Chars(Node):
    type = 'chars'
    mark_id = 0

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        value = escape_string(self.value)
        return f'\'{value}\''

    def assign_word_address(self, address):
        return address + len(self.value)

    def emit_word(self, address, formatter):
        return self.emit_byte(address, formatter)

    def emit_byte(self, address, formatter):
        code = self.value.encode('latin-1')
        return formatter.emit(address, code, self)


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
    REQ = 'req'
    RETURN = 'return'
    RND = 'rnd'
    RNE = 'rne'
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

    def __str__(self):
        if (mark := self.mark) is not None:
            if (address := mark.address) is not None:
                return f'{self.type} {mark} ${address & 0xffff:x}'
            else:
                return f'{self.type} {self.mark}'
        elif (const := self.const) is not None:
            if (value := const.eval()) is not None:
                return f'{self.type} {self.const} ${value & 0xffff:x}'
            else:
                return f'{self.type} {self.const}'
        else:
            return self.type

    def get_op(self):
        return self.ops[self.type]

    def has_data(self):
        return self.mark is not None or self.const is not None

    def eval_data(self):
        if self.mark is not None:
            return self.mark.address
        elif self.const is not None:
            return self.const.eval()

    def assign_address(self, address):
        if not self.has_data(): 
            return address + 1
        elif (data := self.eval_data()) is None:
            return address + 3
        else:
            return self.assign_offset_address(address, data)

    def set_visited(self, marks_to_visit):
        if (const := self.const) is not None:
            # Set all parts of the const expression as visited.
            const.set_visited(marks_to_visit)
        elif (mark := self.mark) is not None:
            # Make sure so to visit the referenced mark later.
            marks_to_visit.add(mark)
            mark.used = True

        # Do not visit commands that follow a final command.
        return self.type not in self.finals

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

    def emit(self, address, formatter):
        code = self.code[self.type]
        if not self.has_data():
            return formatter.emit(address, bytes([code]), self)
        else:
            data = self.eval_data()
            return self.emit_offset(code, address, data, formatter)
            

Command.conditionals = {
    Command.BEQ,
    Command.BNE
}

Command.finals = {
    Command.GOTO,
    Command.RETURN,
    Command.STOP
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

def counter(start):
    def inc(delta=1):
        nonlocal start
        value = start
        start += delta
        return value
    return inc

# c0-c2 are used for word value push operations.
step = counter(0xc3)

Command.code = {
    Command.ADD: step(),
    Command.AND: step(),
    Command.BEQ: step(3) - 1,
    Command.BNE: step(3) - 1,
    Command.GOSUB: step(4),
    Command.CHR: step(),
    Command.CLR: step(),
    Command.DIV: step(),
    Command.DROP: step(),
    Command.DUP: step(),
    Command.EQ: step(),
    Command.FETCH: step(),
    Command.FN: step(),
    Command.FOR: step(),
    Command.GEQ: step(),
    Command.GET: step(),
    Command.GOTO: step(4),
    Command.GT: step(),
    Command.INPUT: step(),
    Command.INT: step(),
    Command.LEQ: step(),
    Command.LT: step(),
    Command.MOD: step(),
    Command.MUL: step(),
    Command.NEQ: step(),
    Command.NEW: step(),
    Command.NEXT: step(),
    Command.NOT: step(),
    Command.ON: step(),
    Command.OR: step(),
    Command.OVER: step(),
    Command.PEEK: step(),
    Command.PICK: step(),
    Command.POKE: step(),
    Command.PRINT: step(),
    Command.REQ: step(),
    Command.RETURN: step(),
    Command.RND: step(),
    Command.RNE: step(),
    Command.ROLL: step(),
    Command.STOP: step(),
    Command.STORE: step(),
    Command.STR: step(),
    Command.SUB: step(),
    Command.SWAP: step(),
    Command.SYS: step(),
}

# Suequence of data blocks that together form a single block of data
# bytes in a compiled program.
class Data(Node):
    type = 'data'
    mark_id = 0

    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def move_symbols(self, statements):
        self.statements.move_symbols(statements)


class Expression(Node):
    type = 'expr'

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def __str__(self):
        expr = ' '.join(str(node) for node in self.nodes)
        if (value := self.eval()) is None:
            return expr
        else:
            return f'${value & 0xffff:x} ({expr})'

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

    def set_visited(self, marks_to_visit):
        for node in self.nodes:
            node.set_visited(marks_to_visit)
        return True

    def eval(self):
        stack = []
        for node in self.nodes:
            if not node.push_to(stack):
                return
        return stack[0]

    def emit(self, address, formatter):
        return self.emit_value(address, formatter)

    def emit_word(self, address, formatter):
        return self.emit_word_value(address, formatter)

    def emit_byte(self, address, formatter):
        return self.emit_byte_value(address, formatter)


class Float(Node):
    type = 'float'
    mark_id = 0

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f'{self.value:.10g}'

    def get_bytes(self):
        number = self.value
        if number >= 0:
            # Mask out sign bit.
            mask = 0x7f
        else:
            # Leave sign bit at 1 and make sure that the mantissa is positive.
            mask = 0xff
            number = -number

        # Map numbers below smallest representable magnitude to zero.
        if number < pow(2.0, -129):
            return bytes(5)

        # Determine exponent and rounded mantissa.
        e = math.floor(math.log2(number)) + 1
        m = math.trunc(number*pow(2.0, 32 - e) + 0.5)

        # Correct possible mantissa overflow due to rounding.
        if m == 0x1_0000_0000:
            e += 1
            m = 0x8000_0000

        if e > 127:
            # Replace number above maximum representable magnitude by the
            # maximum or minimum number.
            return bytes([0xff, 0xff & mask, 0xff, 0xff, 0xff])

        # Get the four bytes of the mantissa.  Note that the sign bit (bit 7 of
        # data[0]) will always be 1.
        data = m.to_bytes(4, 'big')

        # Create the final five byte floating point number.  Center the
        # exponent around 128 and mask out the sign bit for positive numbers.
        return bytes([128 + e, data[0] & mask, data[1], data[2], data[3]])

    def assign_word_address(self, address):
        return address + 5

    def emit_word(self, address, formatter):
        return self.emit_byte(address, formatter)

    def emit_byte(self, address, formatter):
        return formatter.emit(address, self.get_bytes(), self)


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

    def __init__(self, value, *, hex=False):
        super().__init__()
        self.value = to_word(value)
        self.hex = hex

    def __str__(self):
        if self.hex:
            return f'${self.value & 0xffff:x}'
        else:
            return f'{self.value}'

    def assign_address(self, address):
        return self.assign_value_address(address, self.value)

    def eval(self):
        return self.value

    def emit(self, address, formatter):
        return self.emit_value(address, formatter)

    def emit_word(self, address, formatter):
        return self.emit_word_value(address, formatter)

    def emit_byte(self, address, formatter):
        return self.emit_byte_value(address, formatter)


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

    def resolve_mark(self, mark):
        return Macro(self.statements)


class Mark(Node):
    type = 'mark'

    def __init__(self, node, name):
        super().__init__()

        # The node that requested creation of this mark.
        self.node = node

        # Name to use in compiled code listings.
        self.name = name if name is not None else node.make_mark_name()

        # The location of this mark in the compiled program.
        self.address = None

        # The first command after this node, but only if it is GOTO, RETURN, or
        # STOP.
        self.marked = None

        # The code block or data block in which this mark occurs.
        self.block = None

        # The index in the code block or data block nodes where this mark
        # occurs.
        self.index = None

        # The program execution can reach this mark (when in a code block) or
        # the marked data can be accessed (when in a data block).
        self.visited = False

        # This mark is a branch target (when in a code block) or explicitly
        # referenced (when in a data block).
        self.used = False

    def __str__(self):
        return self.name

    def resolve(self):
        return self.node.resolve_mark(self)

    def assign_address(self, address):
        self.address = address
        return address

    def assign_word_address(self, address):
        return self.assign_address(address)

    def assign_byte_address(self, address):
        return self.assign_address(address)

    def set_block_index(self, block, index):
        self.block = block
        self.index = index
        self.visited = False
        self.used = False

    def set_visited(self, marks_to_visit):
        if self.visited:
            # Only continue past this mark if it was not set as visited before.
            return False
        else:
            self.visited = True
            return True

    def visit(self, marks_to_visit):
        self.block.set_visited_from_index(self.index, marks_to_visit)

    def emit(self, address, formatter):
        return formatter.emit_label(address, self)

    def emit_word(self, address, formatter):
        return self.emit(address, formatter)

    def emit_byte(self, address, formatter):
        return self.emit(address, formatter)


class Preamble(Node):
    type = 'preamble'

    def __init__(self, rt):
        self.rt = rt

    def __str__(self):
        return f'call interpreter at ${self.rt:04x}'

    def assign_address(self, address):
        return address + 3

    def emit(self, address, formatter):
        hi, lo = (self.rt >> 8) & 0xff, self.rt & 0xff
        return formatter.emit(address, bytes([0x20, lo, hi]), self)


# Represents either an inline procedure or a procedure in a let definition.
# Such a procedure will be compiled into a separate code block.
class Proc(Node):
    type = 'proc'
    mark_id = 0

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
        self.rt = 0


# A Reference is a node type that encodes a reference to a Mark node.  A symbol
# node results in such a Reference node after the symbol is resolved in the
# current scope.
class Reference(Node):
    type = 'ref'

    def __init__(self, mark):
        self.mark = mark

    def __str__(self):
        return f'{self.mark}'

    def assign_address(self, address):
        if self.mark.address is None:
            # Assume  encoding with largest next address.
            return address + 3
        else:
            return self.assign_value_address(address, self.mark.address)

    def set_visited(self, marks_to_visit):
        self.mark.used = True
        marks_to_visit.add(self.mark)
        return True

    def eval(self):
        return self.mark.address

    def emit(self, address, formatter):
        return self.emit_value(address, formatter)

    def emit_word(self, address, formatter):
        return self.emit_word_value(address, formatter)

    def emit_byte(self, address, formatter):
        return self.emit_byte_value(address, formatter)


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
    mark_id = 0

    def __init__(self, value):
        self.value = value

    def __str__(self):
        value = escape_string(self.value)
        return f'"{value}"'

    def assign_word_address(self, address):
        return address + min(len(self.value), 0xff) + 1

    def emit_word(self, address, formatter):
        return self.emit_byte(address, formatter)

    def emit_byte(self, address, formatter):
        data = bytes([min(len(self.value), 0xff)]) + self.value[:255].encode('latin-1')
        return formatter.emit(address, data, self)


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

    mark_id = 0

    def __init__(self, type, value=None):
        super().__init__()
        self.type = type
        self.value = type if value is None else value

    def __str__(self):
        return self.value
