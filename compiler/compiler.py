
import actions
import blocks
import flow_actions
import formatter
import lexer
import optimizer
import parser


class Compiler:
    def compile(self, file_name, org, rt, fmt):
        # Try to open the source file and read contents.
        with open(file_name, 'r') as source_file:
            src = source_file.read()

        # Phase 1: parse source file contents to Program node.
        lex = lexer.Lexer(src)
        prs = parser.Parser()
        prg = prs.parse(lex)
        prg.rt = rt

        # Phase 2: compile Program to set of code blocks and data blocks.  Use
        # the code reduction rules defined in the rules.txt file and
        # implemented by the Actions class.
        compiled_blocks = []
        opt = optimizer.Optimizer(parser_factory=actions.Actions.parser_factory)
        opt.push_node(prg)
        opt.compile_to(blocks.CodeBlock, compiled_blocks)

        # Phase 3: Optimize execution flow until a fixed point is reached.
        while (recompiled_blocks := self.recompile_blocks(compiled_blocks)) is not None:
            compiled_blocks = recompiled_blocks

        # Phase 4: Assign addresses to all marks.  Repeat this until a fixed
        # point is reached.  Note that the size in bytes of an instruction may
        # depend on mark adresses and can therefore change if any mark address
        # changes.
        org = fmt.emit_begin(org)

        address = org
        while (new_address := self.assign_address(compiled_blocks, org)) != address:
            address = new_address

        # Emit byte code.
        address = org
        for compiled_block in compiled_blocks:
            address = compiled_block.emit(address, fmt)

        fmt.emit_end(org, address)

    def recompile_blocks(self, compiled_blocks):
        # Mark all Mark nodes that are reachable from the program start (first
        # node of first block).
        compiled_blocks[0].visit()

        # Recompiled blocks are collected here.
        recompiled_blocks = []

        # Track if any recompilation led to a different code block or data
        # block.
        changed = False

        # Try to apply verious execution flow optimizations by recompiling each
        # block, taking the status of each Mark node into account.  Use the
        # code reduction rules defined in the flow_rules.txt files and
        # implemented in the FlowActions class.
        for compiled_block in compiled_blocks:
            if not compiled_block.reachable:
                # Leave out non-reachable blocks.  This changes the resulting
                # code.
                changed = True
            else:
                # Recompile the code block or data block.
                recompiled_block = self.recompile_block(compiled_block)

                # Check if the recompiled nodes are different.
                if len(recompiled_block.nodes) != len(compiled_block.nodes) or \
                        any(a is not b for a, b in zip(recompiled_block.nodes, compiled_block.nodes)):
                    # If so, then the code has changed.
                    changed = True

                # Add the recompiled block to the list of all recompiled
                # blocks.
                recompiled_blocks.append(recompiled_block)

        # Only return the new list of blocks if any change occurred.
        if changed:
            return recompiled_blocks

    def recompile_block(self, compiled_block):
        # Recompile the block using the flow actions for optimisation.
        recompiled_blocks = []
        opt = optimizer.Optimizer(parser_factory=flow_actions.FlowActions.parser_factory)
        opt.push_nodes(compiled_block.nodes)
        opt.compile_to(type(compiled_block), recompiled_blocks)

        # Return the recompiled block.  Note that there can be only one block
        # in the list because recompilation cannot introduce new code blocks or
        # new data blocks.
        return recompiled_blocks[0]

    def assign_address(self, blocks, org):
        address = org
        for block in blocks:
            address = block.assign_address(address)
        return address
