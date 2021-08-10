
import tokens
import flow_rules


class FlowActions:
    @classmethod
    def parser_factory(cls):
        actions = cls()
        return flow_rules.ParseStateMachine(actions)

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
        if (marked := cond.mark.marked) is None or \
                marked.get_type() != tokens.Command.GOTO or \
                marked.mark is None:
            # Not a branch to a jump to mark command.  Leave it untouched.
            return False

        # Replace by a branch to the marked jump target.
        optimizer.rewind()
        node = tokens.Command(cond.get_type(), mark=marked.mark).from_node(cond)
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
            type = tokens.Command.BNE
        else:
            type = tokens.Command.BEQ
        node = tokens.Command(type, mark=goto.mark).from_node(cond)
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
