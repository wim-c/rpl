
import ply.lex
import tokens


syntax_tokens = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ':': 'COLON',
    'def': 'DEF',
    'end': 'END',
    'if': 'IF',
    'let': 'LET',
    'then': 'THEN',
}

 
commands = (
    'and',
    'clr',
    'fn',
    'for',
    'get',
    'goto',
    'input',
    'int',
    'next',
    'not',
    'or',
    'peek'
    'poke',
    'print',
    'return',
    'rnd',
    'stop',
    'sys',
)


def make_syntax_token(t):
    t.type = syntax_tokens[t.value]
    t.value = tokens.Token(t)
    return t


def make_command_token(t):
    t.type = 'COMMAND'
    t.value = tokens.Command(t)
    return t


def make_number_token(t):
    if any(char in t.value for char in '.eE'):
        t.type = 'FLOAT'
        t.value = tokens.Float(t)
    else:
        t.type = 'INTEGER'
        t.value = tokens.Integer(t)
    return t


class Lexer(object):
    tokens = (
        'CHARS',
        'COLON',
        'COMMAND',
        'DEF',
        'END',
        'FLOAT',
        'IF',
        'INTEGER',
        'LBRACKET',
        'LET',
        'LPAREN',
        'RBRACKET',
        'RPAREN',
        'STRING',
        'SYMBOL',
        'THEN',
    )

    t_ignore = ' \t\r'

    def __init__(self, txt, name='input'):
        self.errors = []
        self.name = name
        self.lex = ply.lex.lex(module=self)
        self.lex.input(txt)
        self.lex.linepos = -1

    def __iter__(self):
        return self.lex

    def token(self):
        return self.lex.token()

    def t_error(self, t):
        self.errors.append(f'In {self.name} line {t.lineno} column {column(t)}: Unsupported charactor \'{t.value[0]}\'.')
        t.lexer.skip(1)

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.linepos = t.lexpos

    def t_comment(self, t):
        r'(?:--|rem\b)[^\n]*'
        pass

    def t_command_chr(self, t):
        r'chr\$'
        return make_command_token(t)

    def t_command_str(self, t):
        r'str\$'
        return make_command_token(t)

    def t_SYMBOL(self, t):
        r'[a-zA-Z][a-zA-Z0-9]*'
        if t.value in syntax_tokens:
            return make_syntax_token(t)
        if t.value in commands:
            return make_command_token(t)
        t.value = tokens.Symbol(t)
        return t

    def t_STRING(self, t):
        r'"(?:\\\d{1,3}|[^"])*"'
        t.value = tokens.String(t)
        return t

    def t_CHARS(self, t):
        r"'(?:\\\d{1,3}|[^'])*'"
        t.value = tokens.Chars(t)
        return t

    def t_hex(self, t):
        r'-?\$[0-9a-fA-F]+'
        t.type = 'INTEGER'
        if t.value[0] == '-':
            t.value = tokens.Integer(t, -int(t.value[2:], 16))
        else:
            t.value = tokens.Integer(t, int(t.value[1:], 16))
        return t

    def t_number_1(self, t):
        r'-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?'
        return make_number_token(t)

    def t_number_2(self, t):
        r'-?\.\d+(?:[eE][-+]?\d+)?'
        return make_number_token(t)

    def t_command_op(self, t):
        r'<[=>]?|>=?|[-!@#$%^&*+=;\\./]'
        return make_command_token(t)

    def t_syntax_char(self, t):
        r'[()\[\]:]'
        return make_syntax_token(t)
