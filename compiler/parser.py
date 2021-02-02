
import ply.yacc
from lexer import Lexer
import tokens


class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.errors = []
        self.scope = tokens.Scope()
        self.yacc = ply.yacc.yacc(module=self)

    def parse(self, lexer):
        result = self.yacc.parse(lexer=lexer)
        return result

    # --- 

    def p_statements_empty(self, p):
        'statements : '
        p[0] = self.scope.statements()

    def p_statements_simple_statement(self, p):
        'statements : statements simple_statement'
        p[1].append(p[2])
        p[0] = p[1]

    def p_statements_literal(self, p):
        'statements : statements literal'
        p[1].literal(p[2])
        p[0] = p[1]

    def p_statements_definition(self, p):
        'statements : statements block'
        p[1].block(p[2])
        p[0] = p[1]

    def p_statements_label(self, p):
        'statements : statements label'
        p[1].label(p[2])
        p[0] = p[1]

    # ---

    def p_simple_statement(self, p):
        '''simple_statement : COMMAND
                | INTEGER
                | SYMBOL
                | if_statement'''
        p[0] = p[1]

    def p_literal_chars(self, p):
        '''literal : CHARS
                | FLOAT
                | STRING'''
        p[0] = p[1]

    def p_block(self, p):
        '''block : bytes
                | macro
                | proc
                | words'''
        p[0] = p[1]

    # ---

    def p_if_statement(self, p):
        'if_statement : IF statements then_statements END'
        p[0] = tokens.If(p[1], p[2], p[3])

    def p_then_statements_empty(self, p):
        'then_statements : '
        p[0] = None

    def p_then_statements_final(self, p):
        'then_statements : THEN statements'
        p[0] = p[2]

    def p_then_statements(self, p):
        'then_statements : THEN statements IF COLON statements then_statements'
        p[2].append(tokens.If(p[3], p[5], p[6]))
        p[0] = p[2]

    def p_label(self, p):
        'label : SYMBOL COLON'
        p[0] = tokens.Label(p[1])

    def p_bytes(self, p):
        'bytes : LPAREN statements RPAREN'
        p[0] = tokens.Bytes(p[1], p[2])

    def p_macro(self, p):
        'macro : LET statements END'
        p[0] = tokens.Macro(p[1], p[2])

    def p_proc(self, p):
        'proc : DEF statements END'
        p[0] = tokens.Proc(p[1], p[2])

    def p_words(self, p):
        'words : LBRACKET statements RBRACKET'
        p[0] = tokens.Words(p[1], p[2])
