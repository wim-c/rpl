
import rules
import actions


class Reference(object):
    type = 'ref'

    def __init__(self, mark):
        self.mark = mark


class ScopeEnd(object):
    type = 'end'


class Mark(object):
    def __init__(self, symbol, name, node=None, scope=None):
        self.symbol = symbol
        self.name = name
        self.node = node
        self.scope = scope


class Literals(object):
    def __init__(self):
        self.types = {}

    def add_literal(self, node):
        type = node.type
        if type in self.types:
            values = self.types[type]
        else:
            values = {}
            self.types[type] = values
        value = node.value
        if value in values:
            mark = values[value]
        else:
            mark = Mark(node, f'{type}.{len(values)}', node)
            values[value] = mark
        return mark

    def get_literals(self, type):
        return self.types.get(type, [])


class Scope(object):
    next_id = 0

    def __init__(self, optimizer, parent):
        self.id = self.next_id
        self.next_id += 1
        self.optimizer = optimizer
        self.parent = parent
        self.symbols = {}
        self.blocks = {}

    def define(self, symbol, node=None):
        mark = Mark(symbol, f's{self.id}.{name}', node, self)
        name = symbol.value
        if name not in self.symbols:
            self.symbols[name] = mark
        else:
            dup = self.symbols[name].symbol
            self.optimizer.error(node, f'Symbol \'{name}\' already defined at l{dup.line}:c{dup.column}.') 
        return mark

    def find(self, symbol):
        if symbol.value in self.symbols:
            return self.symbols[symbol.value]
        elif self.parent is not None:
            return self.parent.find(symbol)
        else:
            self.optimizer.error(symbol, f'Undefined symbol \'{symbol.value}\'.')

    def add_block(self, node, mark=None):
        type = node.type
        if type in self.blocks:
            blocks = self.blocks[type]
        else:
            blocks = []
            self.blocks[type] = blocks
        if mark is None:
            mark = Mark(node, f's{self.id}.{type}.{len(blocks)}', node, self)
        blocks.append(mark)
        return mark

    def get_blocks(self, type):
        return self.blocks.get(type, [])


class Optimizer(object):
    def __init__(self, literals, scope=None):
        super().__init__()
        
        # Literal values that are interned across all scopes.
        self.literals = literals

        # Current symbol scope.
        self.scope = scope

        # Node stack that represents the optimized code.
        self.nodes = []

        # Parse state stack to keep track of the proper parse state after doing
        # a reduction action.
        self.states = []

        # Stack of node still to consider.  This stack initially will hold
        # statements from a part of the AST.  Reduction actions can push more
        # nodes to process onto this stack during the optimization phase.
        self.node_source = []

        # Instantiate all possible optimizer code reduction actions.  These
        # actions operate on the node and state stacks of this optimizer and
        # can push more nodes to process.
        reductions = new actions.Actions(self)

        # The optimizer state machine that parses the node types of processed
        # nodes.  The parser will return actions to perform from the specified
        # reduction action based on the state transition triggered by a node
        # type.
        self.parser = rules.ParseStateMachine(reductions)

    def begin_scope(self):
        self.scope = Scope(self, self.scope)
        self.push_node(ScopeEnd())

    def end_scope(self):
        self.scope = self.scope.parent

    def current_scope(self):
        return self.scope

    def push_nodes(self, nodes):
        self.node_source.extend(reversed(nodes))

    def push_node(self, node):
        self.node_source.append(node)

    def rewind(self, n):
        # Drop last n nodes from the current node stack.
        nodes = self.nodes[-n:]
        del self.nodes[-n:]

        # Rewind to the parse state before the last n nodes were added.
        state = self.states[-n]
        self.parser.goto(state)
        del self.states[-n:]

        return nodes

    def process_nodes(self):
        while len(self.node_source) > 0:
            node = self.node_source.pop()
            self.process_node(node)

    def process_node(self, node, type=None):
        # Derive the type from the node if it is not explicitly provided.
        if type is None:
            type = node.type

        # Push the node on the node stack.
        self.nodes.append(node)

        # Let the parser process the type.  It returns the previous parse state
        # and a list of actions to trigger.
        state, *actions = self.parser.process(type)

        # Push the previous parse stack on the state stack.
        self.states.append(state)

        # Process all actions until one completes successfully.
        for action in actions:
            if action():
                break
