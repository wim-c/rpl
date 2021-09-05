
import re

class StateBuilder:
    def __init__(self):
        super().__init__()
        self.order = {}
        self.rules = set()
        self.types = set()

        self.states = []
        self.methods = []

        self.state_rules = {}
        self.rules_to_visit = set()

    def close_order(self):
        closed = set()

        def close(s):
            subtypes = self.order[s]
            if s in closed:
                return subtypes
            subs = [sub for sub in subtypes if sub in self.order]
            for sub in subs:
                subtypes.update(close(sub))
            closed.add(s)
            return subtypes

        for sup in self.order:
            close(sup)

    def issubtype(self, a, b):
        return b in self.order and a in self.order[b]

    def isstronger(self, rule_a, rule_b):
        if len(rule_a) > len(rule_b):
            return True
        if len(rule_a) < len(rule_b):
            return False
        for part_a, part_b in zip(rule_a, rule_b):
            if part_a != part_b:
                return self.issubtype(part_a, part_b)
        return False

    def make_state(self, rules):
        rules = tuple(sorted(rules))

        if rules in self.state_rules:
            state = self.state_rules[rules]
        else:
            state = len(self.states)
            self.state_rules[rules] = state
            self.states.append(None)
            self.rules_to_visit.add(rules)

        return state

    def make_edge(self, rules, type):
        new_rules = []
        matching_rules = []

        def insert_match(rule):
            for index in range(len(matching_rules)):
                if self.isstronger(rule[2], matching_rules[index][2]):
                    matching_rules.insert(index, rule)
                    break
            else:
                matching_rules.append(rule)

        def make_new_rule(rule):
            rule_type = rule[2][rule[3]]
            if type == rule_type or self.issubtype(type, rule_type):
                index = rule[3] + 1
                if index < len(rule[2]):
                    new_rules.append((rule[0], rule[1], rule[2], index))
                else:
                    insert_match(rule)

        for rule in self.rules:
            make_new_rule(rule)

        for rule in rules:
            make_new_rule(rule)

        # Check that all matching rules are strictly ordered.
        for index in range(len(matching_rules) - 1):
            if not self.isstronger(matching_rules[index][2], matching_rules[index + 1][2]):
                print(f'ambiguous rules while shifting \'{type}\':')
                for rule in matching_rules:
                    print(f'  {self.methods[rule[0]]}: {rule[2]}')
                break

        # Discard all rules following the first non optional rule
        for index in range(len(matching_rules)):
            if not matching_rules[index][1]:
                del matching_rules[index + 1:]
                break

        if len(matching_rules) > 0 and not matching_rules[-1][1]:
            # This edge will definitely reduce, so there is no need to identify
            # a target state for it.
            state = None
        else:
            # This edge may shift more types so a target state must be
            # identified.
            state = self.make_state(new_rules)

        # return the new state and the methods off triggered rules, most
        # specific first.
        return (type, state, *(rule[0] for rule in matching_rules))

    def visit_rules(self):
        rules = self.rules_to_visit.pop()
        state = self.state_rules[rules]

        # set of types that appear at this point in the any of the rules.
        types = self.types.union(rule[2][rule[3]] for rule in rules)

        # extend this set with all possible subtypes
        for sup in list(types):
            if sup in self.order:
                types.update(self.order[sup])

        # Determine all edge that lead out of this state and order them by type
        # inclusion.
        edges = []

        for type in types:
            edge = self.make_edge(rules, type)
            for index in range(len(edges)):
                if self.issubtype(type, edges[index][0]):
                    edges.insert(index, edge)
                    break
            else:
                edges.append(edge)

        # Prune unnecessary edges (e.g. subtype with the same effect as a
        # supertype).
        self.prune_edges(state, edges)

        self.states[state] = tuple(edges)

    def prune_edges(self, state, edges):
        # Check if two edges lead to the same target (i.e. have the same target
        # state and the same list of actions).
        def same_target(e1, e2):
            return len(e1) == len(e2) and \
                all(e1[i] == e2[i] for i in range(1, len(e1)))

        # Filter out edges that are identical to an edge of a the nearest
        # supertype.  These edges do not add behavior to the state machine.
        for i1 in range(len(edges) - 2, -1, -1):
            # Find the edge for the nearest supertype (if any).
            for i2 in range(i1 + 1, len(edges)):
                if self.issubtype(edges[i1][0], edges[i2][0]):
                    # If both lead to the same state with the same actions,
                    # then remove the edge for the subtype.
                    if same_target(edges[i1], edges[i2]):
                        edges.pop(i1)

                    # Continue to the next edge.
                    break

        # State 0 cannot default to state 0...
        if state == 0:
            return

        # Filter out edges that appear already in state 0 and for which no edge
        # for a supertype exists.
        for i1 in range(len(edges) - 1, -1, -1):
            # Skip if it does not appear in state 0.
            if edges[i1] not in self.states[0]:
                continue

            # Find the edge for the nearest supertype (if any).
            for i2 in range(i1 + 1, len(edges)):
                if self.issubtype(edges[i1][0], edges[i2][0]):
                    # If an edge for a supertype exists then keep this edge.
                    break
            else:
                # No edge for a supertype found.  Remove this edge.
                edges.pop(i1)

    def build_states(self):
        self.make_state([])

        while len(self.rules_to_visit) > 0:
            self.visit_rules()

    def parse_type_line(self, supertype, subtypes):
        if supertype in self.order:
            self.order[supertype].update(subtypes)
        else:
            self.order[supertype] = set(subtypes)

    def parse_rule_line(self, name, optional, rule):
        try:
            index = self.methods.index(name)
        except:
            index = len(self.methods)
            self.methods.append(name)
        self.rules.add((index, optional, tuple(rule), 0))
        self.types.add(rule[0])

    def parse_line(self, line):
        match = re.match(r'\s*(\S+)\s+:>\s+(.+)', line)
        if match is not None:
            return self.parse_type_line(match[1], match[2].split())

        match = re.match(r'\s*(\S+?)(\??)\s+:\s+(.+)', line)
        if match is not None:
            self.parse_rule_line(match[1], match[2] == '?', match[3].split())

    def parse(self, filename):
        with open(filename, 'r') as input:
            for line in input:
                self.parse_line(line)

        self.close_order()
        self.build_states()

    def text(self):
        transitions = ',\n        '.join(str(s) for s in self.states)
        order = ',\n        '.join(f'\'{k}\': {str(v)}' for k, v in self.order.items())
        methods = ',\n            '.join(f'owner.{m}' for m in self.methods)

        return f'''
# This file is generated.  Do not edit.

class ParseStateMachine:
    transitions = (
        {transitions},
    )

    order = {{
        {order}
    }}

    @classmethod
    def matches(cls, type, subject):
        return subject == type or (type in cls.order and subject in cls.order[type])

    def __init__(self, owner):
        super().__init__()

        self.methods = (
            {methods}
        )

        self.state = 0

    @classmethod
    def get_transition(cls, state, subject):
        for transition in cls.transitions[state]:
            if cls.matches(transition[0], subject):
                return transition

    def process(self, subject):
        transition = self.get_transition(self.state, subject)
        if transition is None and self.state != 0:
            transition = self.get_transition(0, subject)

        if transition is None:
            state, self.state = self.state, 0
            return (state,)

        state, self.state = self.state, transition[1]
        return (state, *(self.methods[m] for m in transition[2:]))

    def goto(self, state):
        self.state = state
'''
