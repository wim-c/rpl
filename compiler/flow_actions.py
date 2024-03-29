
import tokens
import flow_rules


class FlowActions:
    # Begin of method section as defined by flow_rules.txt.

    def branch_goto_mark(self, optimizer):
        branch, goto, mark = optimizer.peek(3)
        if branch.mark is not mark or goto.mark is None:
            return False
        elif branch.get_type() == tokens.Command.BEQ:
            branch_type = tokens.Command.BNE
        else:
            branch_type = tokens.Command.BEQ
        node = tokens.Command(branch_type, mark=goto.mark).from_node(branch)
        optimizer.rewind(3)
        optimizer.push_node(mark)
        optimizer.push_node(node)
        return True

    def branch_return_mark(self, optimizer):
        branch, return_, mark = optimizer.peek(3)
        if branch.mark is not mark:
            return False
        elif branch.get_type() == tokens.Command.BEQ:
            branch_type = tokens.Command.RNE
        else:
            branch_type = tokens.Command.REQ
        node = tokens.Command(branch_type).from_node(branch)
        optimizer.rewind(3)
        optimizer.push_node(mark)
        optimizer.push_node(node)
        return True

    def final_command(self, optimizer):
        # Drop a command after a final command.
        optimizer.rewind(1)
        return True

    def final_const(self, optimizer):
        # Drop a constant after a final command.
        optimizer.rewind(1)
        return True

    def final_mark(self, optimizer):
        final, mark = optimizer.peek(2)
        if not mark.used or (marked := mark.marked) is None:
            # Mark will be removed (not used) or it is not followed by a final
            # command.  Either way, this rule does not apply.
            return False
        elif (final_type := final.get_type()) != marked.get_type():
            # Types of final commands are not the same.  Do nothing.
            return False
        elif final_type == tokens.Command.GOTO and \
                (final.mark is not marked.mark or \
                final.const is not marked.const):
            # Final command is a jump but the jump targets are not the same.
            # Do nothing.
            return False

        # Drop the first final command since it will follow directly after the
        # mark as well.
        optimizer.rewind(2)
        optimizer.push_node(mark)
        return True

    def gosub_return(self, optimizer):
        gosub, return_ = optimizer.rewind(2)
        goto = tokens.Command(tokens.Command.GOTO, command=gosub).from_node(gosub)
        optimizer.push_node(goto)
        return True

    def goto_mark(self, optimizer):
        goto, mark = optimizer.peek(2)
        if goto.mark is not mark:
            # Not a jump to the mark that follows it.  Leave it in the code.
            return False

        # Remove a jump to a mark that directly follows it.
        optimizer.rewind(2)
        optimizer.push_node(mark)
        return True

    def negate_branch(self, optimizer):
        _, branch = optimizer.rewind(2)

        # Optimize a not operator on a logical value when followed by a branch.
        if branch.get_type() == tokens.Command.BEQ:
            type = tokens.Command.BNE
        else:
            type = tokens.Command.BEQ

        node = tokens.Command(type, command=branch).from_node(branch)
        optimizer.push_node(node)
        return True

    def push_byte_data(self, optimizer):
        byte_data = optimizer.rewind()

        # Optimize the nodes in the byte data again with a parser that triggers
        # flow actions.
        flow_parser = FlowActions().make_parser()
        opt = optimizer.create_new(flow_parser)
        opt.push_nodes(byte_data.nodes)
        nodes, _ = opt.compile()

        # Only create a new byte data node if the new optimized  content
        # changed.
        if len(byte_data.nodes) != len(nodes) or not all(a is b for a, b in zip(byte_data.nodes, nodes)):
            byte_data = tokens.ByteData(nodes).from_node(byte_data)

        # Emit the byte data to prevent that the byte data is processed again.
        optimizer.emit_node(byte_data)
        return True

    def push_branch(self, optimizer):
        branch = optimizer.peek()
        if (marked := branch.mark.marked) is None:
            # Mark is not followed by a final command.  Nothing to optimize.
            return False
        elif (marked_type := marked.get_type()) != tokens.Command.RETURN and \
                (marked_type != tokens.Command.GOTO or marked.mark is None):
            # Marked command is not a RETURN and not a GOTO with a target mark.
            # Nothing to optimize.
            return False

        # Replace conditional branch by a new conditional node.
        optimizer.rewind()

        # Get the branch type (either BEQ or BNE).
        branch_type = branch.get_type()

        if marked_type == tokens.Command.GOTO:
            # Replace branch to a GOTO by a short circuited branch.
            node = tokens.Command(branch_type, mark=marked.mark)
        elif branch_type == tokens.Command.BEQ:
            # Replace BEQ to a RETURN by a REQ.
            node = tokens.Command(tokens.Command.REQ)
        else:
            # Replace BNE to a RETURN by a RNE.
            node = tokens.Command(tokens.Command.RNE)

        node.from_node(branch)
        optimizer.push_node(node)
        return True

    def push_gosub(self, optimizer):
        gosub = optimizer.peek()
        if (mark := gosub.mark) is None or \
                (marked := mark.marked) is None:
            # Not a gosub to a marked final command.  Leave it untouched.
            return False

        # Drop or replace the gosub command based on the marked target command.
        optimizer.rewind()
        marked_type = marked.get_type()

        if marked_type != tokens.Command.RETURN:
            if marked_type == tokens.Command.GOTO:
                # Replace by a gosub to the marked jump target.
                node = tokens.Command(tokens.Command.GOSUB, command=marked).from_node(gosub)
            else:
                # Replace by the marked (stop) command.
                node = tokens.Command(marked_type).from_node(gosub)

            # Replace the gosub by the new node.
            optimizer.push_node(node)

        return True

    def push_goto(self, optimizer):
        goto = optimizer.peek()
        if (mark := goto.mark) is None or \
                (marked := mark.marked) is None:
            # Not a jump to a marked final command.  Leave it untouched.
            return False

        # Replace by the marked final command.
        optimizer.rewind()
        node = tokens.Command(marked.get_type(), command=marked).from_node(goto)
        optimizer.push_node(node)
        return True

    def push_mark(self, optimizer):
        mark = optimizer.peek()
        if mark.used:
            # Leave used mark in the code.
            return False

        # Remove unused mark.
        optimizer.rewind()
        return True

    def word_branch(self, optimizer):
        word, branch = optimizer.rewind(2)
        type = branch.get_type()
        if (type == tokens.Command.BEQ and word.value == 0) \
                or (type == tokens.Command.BNE and word.value != 0):
            node = tokens.Command(tokens.Command.GOTO, command=branch).from_node(branch)
            optimizer.push_node(node)
        return True

    def word_eq_branch(self, optimizer):
        word, eq, branch = optimizer.peek(3)
        if word.value != 0:
            return False
        elif branch.get_type() == tokens.Command.BEQ:
            type = tokens.Command.BNE
        else:
            type = tokens.Command.BEQ
        node = tokens.Command(type, command=branch).from_node(branch)
        optimizer.rewind(3)
        optimizer.push_node(node)
        return True

    # End of method section as defined by flow_rules.txt.  Helper methods
    # follow below.

    def make_parser(self):
        return flow_rules.ParseStateMachine(self)
