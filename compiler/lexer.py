
import re
import ply.lex
import tokens


# Characters and identifiers that can only represent a syntax token.  These
# will never be part of a parse tree.  Note that the '=' character is not in
# this dictionary since it can represent both a syntax token (in a let
# statement) or a command node.
syntax_tokens = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    ':': 'COLON',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    'CONT': 'CONT',
    'DATA': 'DATA',
    'DEF': 'DEF',
    'ELSE': 'ELSE',
    'END': 'END',
    'IF': 'IF',
    'LET': 'LET',
    'THEN': 'ELSE',     # THEN is a synonym for ELSE in RPL.
    'cont': 'CONT',
    'data': 'DATA',
    'def': 'DEF',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'let': 'LET',
    'then': 'ELSE',     # THEN is a synonym for ELSE in RPL.
}

 
# Identifiers that represent command nodes in a parse tree.
commands = {
    'AND',
    'CLR',
    'DROP',
    'DUP',
    'FN',
    'FOR',
    'GET',
    'GOSUB',
    'GOTO',
    'INPUT',
    'INT',
    'MOD',
    'NEXT',
    'NOT',
    'ON',
    'OR',
    'OVER',
    'PEEK'
    'PICK'
    'POKE',
    'PRINT',
    'RETURN',
    'RND',
    'ROLL',
    'ROT',
    'STOP',
    'SWAP',
    'SYS',
    'XOR',
    'and',
    'clr',
    'drop',
    'dup',
    'fn',
    'for',
    'get',
    'gosub',
    'goto',
    'input',
    'int',
    'mod',
    'next',
    'not',
    'on',
    'or',
    'over',
    'peek',
    'pick',
    'poke',
    'print',
    'return',
    'rnd',
    'roll',
    'rot',
    'stop',
    'swap',
    'sys',
    'xor',
}


aliases = {
    '#': 'dup',
    '$': 'roll',
    '%': 'swap',
    '&': 'gosub',
    '.': 'drop',
    '/\\': '/mod',
    ';': 'over',
    '?': 'print',
    '\\': 'mod',
    '^': 'pick',
}


def make_token(t):
    t.type = syntax_tokens[t.value]
    t.value = tokens.Token(t.type, t.value).from_token(t)
    return t


def make_command(t):
    t.type = 'COMMAND'

    value = t.value.lower()
    value = aliases.get(value, value)

    t.value = tokens.Command(value).from_token(t)
    return t


def make_number(t):
    if re.search('[.eE]', t.value) is None:
        t.type = 'INTEGER'
        t.value = tokens.Integer(int(t.value)).from_token(t)
    else:
        t.type = 'LITERAL'
        t.value = tokens.Float(float(t.value)).from_token(t)
    return t


def make_hex_number(t):
    t.type = 'INTEGER'
    if t.value[0] == '-':
        t.value = tokens.Integer(-int(t.value[2:], 16), hex=True).from_token(t)
    else:
        t.value = tokens.Integer(int(t.value[1:], 16), hex=True).from_token(t)
    return t


def make_text(t):
    def subs(match):
        if match[1] in ('"', "'", '\\'):
            return match[1]
        return chr(int(match[1]) & 0xff)

    quote, text = t.value[0], t.value[1:-1]
    text = re.sub("\\\\('|\"|\\\\|\\d{1,3})", subs, text)

    t.type = 'LITERAL'
    if quote == '"':
        t.value = tokens.String(text).from_token(t)
    else:
        t.value = tokens.Chars(text).from_token(t)
    return t


class Lexer:
    tokens = (
        'COLON',
        'COMMAND',
        'CONT',
        'DATA',
        'DEF',
        'ELSE',
        'END',
        'IF',
        'INTEGER',
        'LBRACKET',
        'LET',
        'LITERAL',
        'LPAREN',
        'RBRACKET',
        'RPAREN',
        'SYMBOL',
    )

    t_ignore = ' \t\r'

    def __init__(self, txt, *, errors=None):
        self.errors = [] if errors is None else errors
        self.lex = ply.lex.lex(module=self)
        self.lex.input(txt)
        self.lex.linepos = -1

    def __iter__(self):
        return self.lex

    def token(self):
        return self.lex.token()

    def t_error(self, t):
        column = t.lexpos - t.lexer.linepos
        self.errors.append(f'l:{t.lineno} c:{column} Unsupported character \'{t.value[0]}\'.')
        t.lexer.skip(1)

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.linepos = t.lexpos

    def t_comment(self, t):
        r'(?:rem\b|REM\b)[^\n]*'
        pass

    def t_command_chr(self, t):
        r'(?:chr|CHR)\$'
        return make_command(t)

    def t_command_str(self, t):
        r'(?:str|STR)\$'
        return make_command(t)

    def t_SYMBOL(self, t):
        r'[_a-zA-Z][_a-zA-Z0-9]*'
        if t.value in syntax_tokens:
            return make_token(t)
        if t.value in commands:
            return make_command(t)
        t.value = tokens.Symbol(t.value).from_token(t)
        return t

    def t_string(self, t):
        '"(?:\\\\(?:"|\'|\\\\|\\d{1,3})|[^\\\\])*?"'
        return make_text(t)

    def t_chars(self, t):
        '\'(?:\\\\(?:"|\'|\\\\|\\d{1,3})|[^\\\\])*?\''
        return make_text(t)

    def t_hex(self, t):
        r'-?\$[0-9a-fA-F]+'
        return make_hex_number(t)

    def t_number_1(self, t):
        r'-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?'
        return make_number(t)

    def t_number_2(self, t):
        r'-?\.\d+(?:[eE][-+]?\d+)?'
        return make_number(t)

    def t_divmod(self, t):
        r'/(?:mod|MOD|\\)'
        return make_command(t)

    def t_command_op(self, t):
        r'<[=>]?|>=?|[-!@#$%^&*+=;\\.?/]'
        return make_command(t)

    def t_syntax_char(self, t):
        r'[(),:\[\]]'
        return make_token(t)
