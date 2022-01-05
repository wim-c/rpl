import tokens
import blocks
import rules


# Class that implements most of the actions from the rules.txt definition.
# Actions that have different behavior in a code context or a data context are
# defined in specialized classes.
class Actions:
    def __init__(self):
        super().__init__()
        self.then_marks = []

    # Begin of method section as defined by rules.txt.

    def compare_not(self, optimizer):
        compare, not_ = optimizer.rewind(2)
        op = compare.get_type()
        if op == tokens.Command.LT:
            op = tokens.Command.GEQ
        elif op == tokens.Command.LEQ:
            op = tokens.Command.GT
        elif op == tokens.Command.NEQ:
            op = tokens.Command.EQ
        elif op == tokens.Command.EQ:
            op = tokens.Command.NEQ
        elif op == tokens.Command.GT:
            op = tokens.Command.LEQ
        elif op == tokens.Command.GEQ:
            op = tokens.Command.LT
        node = tokens.Command(op).from_node(not_)
        optimizer.push_node(node)
        return True

    def const_branch(self, optimizer):
        branch = optimizer.peek()
        if branch.has_data():
            return False
        const, branch = optimizer.rewind(2)
        branch.const = const
        optimizer.push_node(branch)
        return True

    def const_const_binop(self, optimizer):
        const1, const2, binop = optimizer.rewind(3)
        expr = tokens.Expression([const1]).from_node(binop)
        optimizer.push_node(binop)
        optimizer.push_node(const2)
        optimizer.push_node(expr)
        return True

    def const_unop(self, optimizer):
        const, unop = optimizer.rewind(2)
        expr = tokens.Expression([const]).from_node(unop)
        optimizer.push_node(unop)
        optimizer.push_node(expr)
        return True

    def expr_const_binop(self, optimizer):
        expr, const, binop = optimizer.rewind(3)
        expr.from_node(binop).append(const)
        expr.append(binop)
        optimizer.push_node(expr)
        return True

    def expr_expr_binop(self, optimizer):
        expr1, expr2, binop = optimizer.rewind(3)
        expr1.from_node(binop).extend(expr2.nodes)
        expr1.append(binop)
        optimizer.push_node(expr1)
        return True

    def expr_unop(self, optimizer):
        expr, unop = optimizer.rewind(2)
        expr.from_node(unop).append(unop)
        optimizer.push_node(expr)
        return True

    # Compile a data node defined by a let node.
    def let_data(self, optimizer):
        let, data = optimizer.rewind(2)
        mark = optimizer.scope.get_mark(let.symbol)
        self.compile_data(mark, data.statements, optimizer)
        return True

    # Macros are expanded and compiled in place only.  The macro definition
    # from a let nore needs no processing at its point of definition.
    def let_macro(self, optimizer):
        optimizer.rewind(2)
        return True

    # Compile a procedure node defined by a let node.
    def let_proc(self, optimizer):
        let, proc = optimizer.rewind(2)
        mark = optimizer.scope.get_mark(let.symbol)
        self.compile_proc(mark, proc.statements, optimizer)
        return True

    def mark_final(self, optimizer):
        mark, final = optimizer.peek(2)
        if mark.marked is final:
            return False
        mark, final = optimizer.rewind(2)
        mark.marked = final
        optimizer.push_node(final)
        optimizer.push_node(mark)
        return True

    def mark_goto(self, optimizer):
        goto = optimizer.peek()
        return goto.has_data() and self.mark_final(optimizer)

    def mark_mark(self, optimizer):
        mark1, mark2 = optimizer.peek(2)
        if mark1.marked is mark2.marked:
            return False
        mark1, mark2 = optimizer.rewind(2)
        mark1.marked = mark2.marked
        optimizer.push_node(mark2)
        optimizer.push_node(mark1)
        return True

    def push_END(self, optimizer):
        optimizer.rewind()
        optimizer.close_scope()
        return True

    def push_THEN(self, optimizer):
        optimizer.rewind()
        self.then_marks.pop()
        return True

    def push_contif(self, optimizer):
        contif = optimizer.rewind()
        mark = self.then_marks[-1]
        beq = tokens.Command(tokens.Command.BEQ, mark=mark).from_node(contif)
        optimizer.push_node(beq)
        return True

    # Reduce a data block
    def push_data(self, optimizer):
        data = optimizer.rewind()
        mark = data.mark()
        self.compile_data(mark, data.statements, optimizer)
        ref = mark.resolve().from_node(data)
        optimizer.push_node(ref)
        return True

    def push_if(self, optimizer):
        if_ = optimizer.rewind()

        # Create mark beyond END of if statement.
        self.push_then_mark(optimizer)
        end_mark = self.then_marks[-1]

        # Push statements block followed by a jump to the end mark.
        def push_if_block(block):
            goto = tokens.Command(tokens.Command.GOTO, mark=end_mark)
            optimizer.push_node(goto)
            optimizer.push_node(block)

        # Push all statements blocks but the first and prepare a THEN mark for
        # each of them.
        for block in if_.blocks[:0:-1]:
            push_if_block(block)
            self.push_then_mark(optimizer)

        # Push first statements block and a conditional jump (if false) to the
        # current THEN mark.  This will be the end mark if there are no THEN
        # statements blocks.
        mark = self.then_marks[-1]
        beq = tokens.Command(tokens.Command.BEQ, mark=mark).from_node(if_)
        push_if_block(if_.blocks[0])
        optimizer.push_node(beq)

        return True

    def push_label(self, optimizer):
        label = optimizer.rewind()

        # A label definition is not a referecne.  Do not report an error if the
        # mark is not found.  This can happen when a label has more than one
        # definitions, which will be reported as an error when the label is
        # defined.
        mark = optimizer.scope.get_mark(label.symbol, required=False)

        if mark is not None:
            optimizer.push_node(mark)

        return True

    def push_let(self, optimizer):
        let = optimizer.peek()

        if optimizer.scope.get_mark(let.symbol, required=False) is None:
            # Drop this let node since its symbol is not defined.  An error has
            # already been reported in that case.
            optimizer.rewind()
            return True

        # Push the bound node to trigger a specific rule based on its type.
        # This node will be a data node, proc node, or macro node.
        optimizer.push_node(let.definition)

    # Reduce a Macro node.
    def push_macro(self, optimizer):
        macro = optimizer.rewind()
        end = tokens.Token(tokens.Token.END)
        optimizer.push_node(end)
        optimizer.push_node(macro.statements)
        optimizer.open_scope()
        return True

    # Reduce an anonymous procedure.
    def push_proc(self, optimizer):
        proc = optimizer.rewind()

        # Create an implicit mark for the procedure.
        mark = proc.mark()

        # Compile the procedure and add resulting blocks to the optimizer.
        self.compile_proc(mark, proc.statements, optimizer)

        # Push a reference to the procedure's mark.
        ref = mark.resolve().from_node(proc)
        optimizer.push_node(ref)
        return True

    # Reduce a program.
    def push_program(self, optimizer):
        program = optimizer.rewind()

        # End with a mark for any contif statement and an implicit stop
        # statement.
        stop = tokens.Command(tokens.Command.STOP)
        optimizer.push_node(stop)
        self.push_then_mark(optimizer)

        # Optimize the program body statements.
        optimizer.push_node(program.statements)

        # Begin the program with an implicit preamble to invoke the byte code
        # interpreter at the provided runtime address..
        preamble = tokens.Preamble(program.rt)
        optimizer.push_node(preamble)

        # Create program level scope.
        optimizer.open_scope()

        # Program node has been reduced.
        return True

    # Reduce a Statements node.
    def push_statements(self, optimizer):
        scope = optimizer.scope
        statements = optimizer.rewind()

        for label in statements.labels:
            scope.add_label(label)

        for definition in statements.definitions:
            scope.add_definition(definition)

        optimizer.push_nodes(statements.statements)
        return True

    def push_symbol(self, optimizer):
        symbol = optimizer.rewind()
        mark = optimizer.scope.get_mark(symbol)

        if mark is not None:
            value = mark.resolve().from_node(symbol)
            optimizer.push_node(value)

        return True

    def ref_branch(self, optimizer):
        branch = optimizer.peek()
        if branch.has_data():
            return False
        ref, branch = optimizer.rewind(2)
        branch.mark = ref.mark
        optimizer.push_node(branch)
        return True

    def word_unop(self, optimizer):
        word, command = optimizer.rewind(2)
        value = command.get_op()(word.value)
        word = tokens.Integer(value, hex=word.hex).from_node(command)
        optimizer.push_node(word)
        return True

    def word_word_binop(self, optimizer):
        word1, word2, command = optimizer.rewind(3)
        value = command.get_op()(word1.value, word2.value)
        word = tokens.Integer(value, hex=word1.hex or word2.hex).from_node(command)
        optimizer.push_node(word)
        return True

    #
    # End of method section as defined by rules.txt.  Helper methods follow
    # below.
    #

    # Ctreate a parser instance that can be used by an optimizer.  The parser
    # triggers methods on self according to the rules in rules.txt.
    def make_parser(self):
        return rules.ParseStateMachine(self)

    # Helper method to setup a terget for a conditional branch.
    def push_then_mark(self, optimizer):
        then = tokens.Token(tokens.Token.THEN)
        mark = then.mark()
        self.then_marks.append(mark)
        optimizer.push_node(then)
        optimizer.push_node(mark)

    # Helper method to compile a data node with a separate optimizer.
    def compile_data(self, mark, statements, optimizer):
        # Create new optimizer to compile data statements
        actions = DataActions()
        parser = actions.make_parser()
        opt = optimizer.create_new(parser)

        # Push a final THEN mark as target for any CONT IF statement.
        actions.push_then_mark(opt)

        # Compile the data statements to a DataBlock.  Add all blocks to the
        # optimizer.
        opt.push_node(statements)
        opt.push_node(mark)
        opt.compile_to(blocks.DataBlock, optimizer.blocks)

    # Helper method to compile a proc node with a separate optimizer.
    def compile_proc(self, mark, statements, optimizer):
        # Create new optimizer to compile data statements
        actions = ProcActions()
        parser = actions.make_parser()
        opt = optimizer.create_new(parser)

        # Add an implicit return statement to the procedure.
        return_ = tokens.Command(tokens.Command.RETURN)
        opt.push_node(return_)

        # Push a final THEN mark as target for any CONT IF statement.
        actions.push_then_mark(opt)

        # Compile the procedure statements to a CodeBlock.  Add all blocks to
        # the optimizer.
        opt.push_node(statements)
        opt.push_node(mark)
        opt.compile_to(blocks.CodeBlock, optimizer.blocks)


# This class implements the actions that have specific behavior in a code
# context.
class ProcActions(Actions):
    # Begin of method section as defined by rules.txt.

    def push_bytes(self, optimizer):
        bytes = optimizer.rewind()
        self.compile_as_data(bytes, optimizer)
        return True

    def push_literal(self, optimizer):
        literal = optimizer.rewind()
        self.compile_as_data(literal, optimizer)
        return True

    # End of method section as defined by rules.txt.  Helper methods follow
    # below.

    # Helper method to wrap a single node in a Data node and compile it.  This
    # is used to compile string, chars, float, and bytes nodes in a procedure
    # context.
    def compile_as_data(self, node, optimizer):
        mark = node.mark()

        # Create a Statements node with a single statement.
        statements = tokens.Statements()
        statements.append(node)

        # Compile a data block with from this statement.
        self.compile_data(mark, statements, optimizer)

        # Push a reference to the data block
        ref = mark.resolve().from_node(node)
        optimizer.push_node(ref)
        return True


# This class implements the actions that have specific behavior in a data
# context.
class DataActions(Actions):
    # Begin of method section as defined by rules.txt.

    def push_bytes(self, optimizer):
        bytes = optimizer.rewind()

        # Create a new optimizer to compile bytes node statements.
        actions = DataActions()
        parser = actions.make_parser()
        opt = optimizer.create_new(parser)

        # Create a final THEN mark as target for any CONT IF statement.
        # TODO: This mark is not optimized away if it is not used?  Fix.
        actions.push_then_mark(opt)

        # Compile the bytes node statements.
        opt.push_node(bytes.statements)
        nodes, blocks = opt.compile()

        # Add indirect compiled blocks to the list of optimized blocks.
        optimizer.extend_blocks(blocks)

        # Create and push a new ByteData node.
        byte_data = tokens.ByteData(nodes).from_node(bytes)
        optimizer.push_node(byte_data)
        return True

    def push_literal(self, optimizer):
        pass

    # End of method section as defined by rules.txt.
