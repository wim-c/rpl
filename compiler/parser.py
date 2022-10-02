
import ply.yacc
from lexer import Lexer
import tokens


class Parser:
    tokens = Lexer.tokens

    def __init__(self, *, errors=None):
        self.yacc = ply.yacc.yacc(module=self)
        self.errors = [] if errors is None else errors

    def parse(self, lexer):
        return self.yacc.parse(lexer=lexer)

    def p_error(self, p):
        if p is None:
            self.errors.append('Unexpected end of file.')
        else:
            self.errors.append(f'l:{p.value.line} c:{p.value.column} Syntax error at \'{p.value}\'.')

    # --- 

    def p_program(self, p):
        'program : statements'
        p[0] = tokens.Program(p[1]).from_node(p[1])

    # ---

    def p_statements(self, p):
        'statements : '
        p[0] = tokens.Statements()

    def p_statements_statement(self, p):
        'statements : statements statement'
        p[1].append(p[2])
        p[0] = p[1]

    # ---

    def p_statement(self, p):
        '''statement : COMMAND
                | INTEGER
                | LITERAL
                | SYMBOL
                | bytes
                | contif
                | data
                | if
                | label
                | let
                | proc'''
        p[0] = p[1]

    # ---

    def p_data_bytes(self, p):
        'bytes : LPAREN statements RPAREN'
        p[0] = tokens.Bytes(p[2]).from_node(p[1])

    def p_contif(self, p):
        'contif : CONT IF'
        p[0] = tokens.Command(tokens.Command.CONTIF).from_node(p[1])

    def p_data(self, p):
        '''data : DATA statements END
                | LBRACKET statements RBRACKET'''
        p[0] = tokens.Data(p[2]).from_node(p[1])

    def p_if(self, p):
        'if : IF if_blocks END'
        p[0] = tokens.If(p[2]).from_node(p[1])

    def p_label(self, p):
        'label : SYMBOL COLON'
        p[0] = tokens.Label(p[1]).from_node(p[1])

    def p_let(self, p):
        'let : LET SYMBOL definition'
        p[0] = tokens.Let(p[2], p[3]).from_node(p[1])

    def p_proc(self, p):
        'proc : DEF statements END'
        p[0] = tokens.Proc(p[2]).from_node(p[1])

    # ---

    def p_if_blocks(self, p):
        'if_blocks : statements'
        p[0] = [p[1]]

    def p_if_blocks_then(self, p):
        'if_blocks : if_blocks ELSE statements'
        p[1].append(p[3])
        p[0] = p[1]

    def p_definition(self, p):
        '''definition : data
                | macro
                | proc'''
        p[0] = p[1]

    def p_definition_data(self, p):
        '''definition : LITERAL
                | bytes'''
        statements = tokens.Statements()
        statements.append(p[1])
        p[0] = tokens.Data(statements)

    # ---

    def p_macro(self, p):
        'macro : COLON statements END'
        p[0] = tokens.Macro(p[2]).from_node(p[1])
