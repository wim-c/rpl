
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
                | SYMBOL
                | data
                | if
                | label
                | let
                | proc'''
        p[0] = p[1]

    # ---

    def p_data(self, p):
        'data : DATA data_parts END'
        p[0] = tokens.Data(p[2]).from_node(p[1])

    def p_data_data_part(self, p):
        'data : data_part'
        p[0] = tokens.Data([p[1]]).from_node(p[1])

    def p_if(self, p):
        'if : IF if_blocks END'
        p[0] = tokens.If(p[2]).from_node(p[1])

    def p_label(self, p):
        'label : SYMBOL COLON'
        p[0] = tokens.Label(p[1]).from_node(p[1])

    def p_let(self, p):
        'let : LET SYMBOL definition'
        p[0] = tokens.Let(p[2], p[3]).from_node(p[1])

    # ---

    def p_data_parts(self, p):
        'data_parts : data_part'
        p[0] = [p[1]]

    def p_data_parts_data_part(self, p):
        'data_parts : data_parts data_part'
        p[1].append(p[2])
        p[0] = p[1]

    def p_data_part(self, p):
        '''data_part : LITERAL
                | bytes
                | words'''
        p[0] = p[1]

    def p_if_blocks(self, p):
        'if_blocks : if_block'
        p[0] = [p[1]]

    def p_if_blocks_then(self, p):
        'if_blocks : if_blocks THEN if_block'
        p[1].append(p[3])
        p[0] = p[1]

    def p_definition(self, p):
        '''definition : data
                | macro
                | proc'''
        p[0] = p[1]

    # ---

    def p_bytes(self, p):
        'bytes : LPAREN statements RPAREN'
        p[0] = tokens.Bytes(p[2]).from_node(p[1])

    def p_words(self, p):
        'words : LBRACKET statements RBRACKET'
        p[0] = tokens.Words(p[2]).from_node(p[1])

    def p_if_block(self, p):
        'if_block : statements'
        p[0] = p[1]

    def p_if_block_cont_if(self, p):
        'if_block : if_block CONT IF statements'
        p[1].append(tokens.Command(tokens.Command.CONTIF).from_node(p[2]))
        p[1].extend(p[4])
        p[0] = p[1]

    def p_macro(self, p):
        'macro : COLON statements END'
        p[0] = tokens.Macro(p[2]).from_node(p[1])

    def p_proc(self, p):
        'proc : DEF statements END'
        p[0] = tokens.Proc(p[2]).from_node(p[1])
