
import tokens
import flow_rules


class FlowActions:
    def make_parser(self):
        return flow_rules.ParseStateMachine(self)

    def push_mark(self, optimizer):
        mark = optimizer.peek()
        if mark.used:
            # Leave used mark in the code.
            return False

        # Remove unused mark.
        optimizer.rewind()
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

    def push_cond(self, optimizer):
        cond = optimizer.peek()
        if (marked := cond.mark.marked) is None:
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
        cond_type = cond.get_type()

        if marked_type == tokens.Command.GOTO:
            # Replace branch to a GOTO by a short circuited branch.
            node = tokens.Command(cond_type, mark=marked.mark)
        elif cond_type == tokens.Command.BEQ:
            # Replace BEQ to a RETURN by a REQ.
            node = tokens.Command(tokens.Command.REQ)
        else:
            # Replace BNE to a RETURN by a RNE.
            node = tokens.Command(tokens.Command.RNE)

        node.from_node(cond)
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

    def goto_mark(self, optimizer):
        goto, mark = optimizer.peek(2)
        if goto.mark is not mark:
            # Not a jump to the mark that follows it.  Leave it in the code.
            return False

        # Remove a jump to a mark that directly follows it.
        optimizer.rewind(2)
        optimizer.push_node(mark)
        return True

    def cond_goto_mark(self, optimizer):
        cond, goto, mark = optimizer.peek(3)
        if cond.mark is not mark or goto.mark is None:
            return False
        elif cond.get_type() == tokens.Command.BEQ:
            cond_type = tokens.Command.BNE
        else:
            cond_type = tokens.Command.BEQ
        node = tokens.Command(cond_type, mark=goto.mark).from_node(cond)
        optimizer.rewind(3)
        optimizer.push_node(mark)
        optimizer.push_node(node)
        return True

    def cond_return_mark(self, optimizer):
        cond, return_, mark = optimizer.peek(3)
        if cond.mark is not mark:
            return False
        elif cond.get_type() == tokens.Command.BEQ:
            cond_type = tokens.Command.RNE
        else:
            cond_type = tokens.Command.REQ
        node = tokens.Command(cond_type).from_node(cond)
        optimizer.rewind(3)
        optimizer.push_node(mark)
        optimizer.push_node(node)
        return True

    def gosub_return(self, optimizer):
        gosub, return_ = optimizer.rewind(2)
        goto = tokens.Command(tokens.Command.GOTO, command=gosub).from_node(gosub)
        optimizer.push_node(goto)
        return True

    def word_cond(self, optimizer):
        word, cond = optimizer.rewind(2)
        type = cond.get_type()
        if (type == tokens.Command.BEQ and word.value == 0) or \
                (type == tokens.Command.BNE and word.value != 0):
            node = tokens.Command(tokens.Command.GOTO, command=cond).from_node(cond)
            optimizer.push_node(node)
        return True

    def word_eq_cond(self, optimizer):
        word, eq, cond = optimizer.peek(3)
        if word.value != 0:
            return False
        elif cond.get_type() == tokens.Command.BEQ:
            type = tokens.Command.BNE
        else:
            type = tokens.Command.BEQ
        node = tokens.Command(type, command=cond).from_node(cond)
        optimizer.rewind(3)
        optimizer.push_node(node)
        return True

    def word_neq_cond(self, optimizer):
        word, neq, cond = optimizer.peek(3)
        if word.value != 0:
            return False
        optimizer.rewind(3)
        optimizer.push_node(cond)
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
