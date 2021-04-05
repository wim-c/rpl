
import ply.yacc
from lexer import Lexer
import tokens


class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.yacc = ply.yacc.yacc(module=self)

    def parse(self, lexer):
        result = self.yacc.parse(lexer=lexer)
        return result

    # --- 

    def p_statements(self, p):
        'statements : '
        p[0] = []

    def p_statements_statement(self, p):
        'statements : statements statement'
        p[1].append(p[2])
        p[0] = p[1]

    # ---

    def p_statement(self, p):
        '''statement : COMMAND
                | IS
                | LITERAL
                | SYMBOL
                | bytes
                | if
                | label
                | let
                | proc
                | words'''
        p[0] = p[1]

    # ---

    def p_bytes(self, p):
        'bytes : LPAREN statements RPAREN'
        p[0] = tokens.Bytes(p[1], p[2])

    def p_if(self, p):
        'if : IF if_blocks END'
        p[0] = tokens.If(p[1], p[2])

    def p_label(self, p):
        'label : SYMBOL COLON'
        p[0] = tokens.Label(p[1])

    def p_let(self, p):
        'let : LET let_blocks END'
        p[0] = tokens.Let(p[1], p[2])

    def p_proc(self, p):
        'proc : DEF statements END'
        p[0] = tokens.Proc(p[1], p[2])

    def p_words(self, p):
        'words : LBRACKET statements RBRACKET'
        p[0] = tokens.Words(p[1], p[2])

    # ---

    def p_if_blocks(self, p):
        'if_blocks : if_statements'
        p[0] = [p[1]]

    def p_if_blocks_then(self, p):
        'if_blocks : if_blocks THEN if_statements'
        p[1].append(p[3])
        p[0] = p[1]

    def p_let_blocks(self, p):
        'let_blocks : definition'
        p[0] = [p[1]]

    def p_let_blocks_comma(self, p):
        'let_blocks : let_blocks COMMA definition'
        p[1].append(p[3])
        p[0] = p[1]

    # ---

    def p_if_statements(self, p):
        'if_statements : statements'
        p[0] = p[1]

    def p_if_statements_cont_if(self, p):
        'if_statements : if_statements CONT IF statements'
        p[1].append(tokens.Command(p[2], 'contif'))
        p[1].extend(p[4])
        p[0] = p[1]

    def p_definition_is(self, p):
        'definition : SYMBOL IS statements'
        p[0] = (p[1], tokens.Macro(p[2], p[3]))

    def p_definition_data(self, p):
        'definition : SYMBOL DATA statements'
        p[0] = (p[1], tokens.Words(p[2], p[3]))

    def p_definition_data_2(self, p):
        '''definition : SYMBOL bytes
                | SYMBOL words'''
        p[0] = (p[1], p[2])

    def p_definition_def(self, p):
        'definition : SYMBOL DEF statements'
        p[0] = (p[1], tokens.Proc(p[2], p[3]))
