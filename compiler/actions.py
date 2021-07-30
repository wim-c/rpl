
import tokens
import blocks

# Class that implements all actions from the rules.txt definition.
class Actions:
    def __init__(self):
        super().__init__()
        self.then_marks = []

    def push_bytes(self, optimizer):
        bytes = optimizer.rewind()

        opt = optimizer.create_new()
        opt.push_node(bytes.statements)
        nodes, blocks = opt.compile()

        byte_block = tokens.ByteData(nodes).from_node(bytes)
        optimizer.emit_node(byte_block)
        optimizer.extend_blocks(blocks)
        return True

    def push_words(self, optimizer):
        words = optimizer.rewind()

        opt = optimizer.create_new()
        opt.push_node(words.statements)
        nodes, blocks = opt.compile()

        optimizer.emit_nodes(nodes)
        optimizer.extend_blocks(blocks)
        return True

    def push_contif(self, optimizer):
        optimizer.rewind()
        mark = self.then_marks[-1]
        beq = tokens.Command(tokens.Command.BEQ, mark=mark)
        optimizer.push_node(beq)
        return True

    # Reduce a procedure.
    def push_proc(self, optimizer):
        proc = optimizer.rewind()
        return_ = tokens.Command(tokens.Command.RETURN)
        mark = proc.mark().from_node(proc)

        opt = optimizer.create_new()
        opt.push_node(return_)
        opt.push_node(proc.statements)
        opt.push_node(mark)
        opt.compile_to(blocks.CodeBlock, optimizer.blocks)

        ref = mark.resolve().from_node(proc)
        optimizer.push_node(ref)
        return True

    # Reduce a data block
    def push_data(self, optimizer):
        data = optimizer.rewind()
        mark = data.mark().from_node(data)

        opt = optimizer.create_new()
        opt.push_nodes(data.blocks)
        opt.push_node(mark)
        opt.compile_to(blocks.DataBlock, optimizer.blocks)

        ref = mark.resolve().from_node(data)
        optimizer.push_node(ref)
        return True

    # Reduce a program.
    def push_program(self, optimizer):
        program = optimizer.rewind()

        # End with an implicit stop statement.
        node = tokens.Command(tokens.Command.STOP)
        optimizer.push_node(node)

        # Optimize the program body statements.
        optimizer.push_node(program.statements)

        # Begin the program with an implicit preamble to invoke the byte code
        # interpreter.
        preamble = tokens.Preamble()
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

    # Reduce a Macro node.
    def push_macro(self, optimizer):
        macro = optimizer.rewind()
        end = tokens.Token(tokens.Token.END)
        optimizer.push_node(end)
        optimizer.push_node(macro.statements)
        optimizer.open_scope()
        return True
        
    def push_THEN(self, optimizer):
        optimizer.rewind()
        self.then_marks.pop()
        return True

    def push_END(self, optimizer):
        optimizer.rewind()
        optimizer.close_scope()
        return True
            
    def push_label(self, optimizer):
        label = optimizer.rewind()
        mark = optimizer.scope.get_mark(label.symbol)

        if mark is not None:
            optimizer.push_node(mark)

        return True

    def push_symbol(self, optimizer):
        symbol = optimizer.rewind()
        mark = optimizer.scope.get_mark(symbol)

        if mark is not None:
            value = mark.resolve().from_node(symbol)
            optimizer.push_node(value)

        return True
        
    def push_define_macro(self, optimizer):
        optimizer.rewind()
        return True

    def push_define_proc(self, optimizer):
        let = optimizer.rewind()
        mark = optimizer.scope.get_mark(let.symbol)

        if mark is not None:
            return_ = tokens.Command(tokens.Command.RETURN)
            opt = optimizer.create_new()
            opt.push_node(return_)
            opt.push_node(let.definition.statements)
            opt.push_node(mark)
            opt.compile_to(blocks.CodeBlock, optimizer.blocks)

        return True

    def push_define_data(self, optimizer):
        let = optimizer.rewind()
        mark = optimizer.scope.get_mark(let.symbol)

        if mark is not None:
            opt = optimizer.create_new()
            opt.push_nodes(let.definition.blocks)
            opt.push_node(mark)
            opt.compile_to(blocks.DataBlock, optimizer.blocks)

        return True

    def push_if(self, optimizer):
        if_ = optimizer.rewind()

        def push_then_mark():
            then = tokens.Token(tokens.Token.THEN)
            mark = then.mark()
            self.then_marks.append(mark)
            optimizer.push_node(then)
            optimizer.push_node(mark)

        # Create mark beyond END of if statement.
        push_then_mark()
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
            push_then_mark()

        # Push first statements block and a conditional jump (if false) to the
        # current THEN mark.  This will be the end mark if there are no THEN
        # statements blocks.
        mark = self.then_marks[-1]
        beq = tokens.Command(tokens.Command.BEQ, mark=mark)
        push_if_block(if_.blocks[0])
        optimizer.push_node(beq)

        return True
