
import rules
import scope
import actions


class ErrorMessage:
    def __init__(self, node, message):
        super().__init__()
        self.node = node
        self.message = message

    def __str__(self):
        line = self.node.line
        column = self.node.column
        return f'l:{line} c:{column} {self.message}'


class Optimizer:
    def __init__(self, *, blocks=None, errors=None):
        super().__init__()
        
        # All compile errors are collected here.
        self.errors = errors if errors is not None else []

        # All emited code blocks are collected here.
        self.blocks = blocks if blocks is not None else []

        # Current symbol scope.
        self.scope = None

        # Node stack that represents the optimized code so far.
        self.nodes = []

        # Parse state stack to keep track of the proper parse state after doing
        # a reduction action.
        self.states = []

        # Stack of nodes still to consider.  This stack initially will hold
        # statements from a part of the AST.  Reduction actions can push more
        # nodes to process onto this stack during the optimization phase.
        self.node_source = []

        # Instantiate all possible optimizer code reduction actions.  These
        # actions operate on the node and state stacks of this optimizer and
        # can push more nodes to process.
        reductions = actions.Actions()

        # The optimizer state machine that parses the node types of processed
        # nodes.  The parser will return actions to perform from the specified
        # reduction action based on the state transition triggered by a node
        # type.
        self.parser = rules.ParseStateMachine(reductions)

    # Create an optimizer instance with a nested scope.  This means that all
    # symbols currently in scope are visible to the new optimizer, but it
    # cannot add to the current scope.
    def create_new(self):
        opt = Optimizer(errors=self.errors)
        opt.scope = scope.Scope(opt, self.scope)
        return opt

    def add_error(self, node, msg):
        self.errors.append(ErrorMessage(node, msg))

    # Open a new scope.  The current scope (if any) will be set as its parent
    # scope.
    def open_scope(self):
        self.scope = scope.Scope(self, self.scope)

    # Replace the current scope by its parent scope or None if it is the top
    # level scope.
    def close_scope(self):
        self.scope = self.scope.parent

    # Push a list of nodes onto the stack of nodes to be processed next.  The
    # first node of this list is popped first from that stack.
    def push_nodes(self, nodes):
        self.node_source.extend(reversed(nodes))

    # Push a single node onto the stack of nodes to be processed next.
    def push_node(self, node):
        self.node_source.append(node)

    # Emit a single node, bypassing all reduction rules.  This will reset the
    # parser's state.
    def emit_node(self, node):
        self.nodes.append(node)
        self.states.clear()
        self.parser.goto(0)

    # Emit a sequence of nodes, bypassing all reduction rules.  This will reset
    # the parser's state.
    def emit_nodes(self, nodes):
        self.nodes.extend(nodes)
        self.states.clear()
        self.parser.goto(0)

    # Return given number of nodes from the optimized nodes stack.  Does not
    # pop these nodes.
    def peek(self, n=None):
        if n is None:
            return self.nodes[-1]
        else:
            return self.nodes[-n:]

    # Pop and return n nodes from the optimized nodes stack and reset the parse
    # state accordingly.
    def rewind(self, n=None):
        # Drop last n nodes from the current node stack.
        if n is not None:
            # Return a list of nodes.
            nodes = self.nodes[-n:]
            del self.nodes[-n:]
        else:
            n = 1
            # Return a single node.
            nodes = self.nodes.pop()

        # Rewind to the parse state before the last n nodes were added.
        state = self.states[-n]
        self.parser.goto(state)
        del self.states[-n:]

        return nodes

    def process_nodes(self):
        while len(self.node_source) > 0:
            node = self.node_source.pop()
            self.process_node(node)

    def process_node(self, node):
        # Push the node on the node stack.
        self.nodes.append(node)

        # Let the parser process the type.  It returns the previous parse state
        # and a list of actions to trigger.
        type = node.get_type()
        state, *actions = self.parser.process(type)

        # Push the previous parse stack on the state stack.
        self.states.append(state)

        # Process all actions until one completes successfully.
        for action in actions:
            if action(self):
                break

    def append_block(self, block):
        self.blocks.append(block)

    def extend_blocks(self, blocks):
        self.blocks.extend(blocks)

    def compile(self):
        # Process all source nodes.
        self.process_nodes()

        # Return optimized nodes and all additinal blocks.
        return self.nodes, self.blocks

    # Helper to compile to a specific block type and add the compiled block and
    # all additional blocks to a specified optimizer.
    def compile_to(self, cls, blocks):
        self.process_nodes()
        block = cls(self.nodes)
        blocks.append(block)
        blocks.extend(self.blocks)
