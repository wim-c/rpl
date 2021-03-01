
import re

class StateBuilder(object):
    def __init__(self):
        super().__init__()
        self.order = {}
        self.rules = set()
        self.types = set()

        self.states = []

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

    def make_target(self, rules, type):
        new_rules = []
        matching_rules = []
        matching_names = []

        def insert_match(rule):
            for index in range(len(matching_rules)):
                if self.isstronger(rule[1], matching_rules[index]):
                    matching_rules.insert(index, rule[1])
                    matching_names.insert(index, rule[0])
                    break
            else:
                matching_rules.append(rule[1])
                matching_names.append(rule[0])

        def make_new_rule(rule):
            rule_type = rule[1][rule[2]]
            if type == rule_type or self.issubtype(type, rule_type):
                index = rule[2] + 1
                if index < len(rule[1]):
                    new_rules.append((rule[0], rule[1], index))
                else:
                    insert_match(rule)

        for rule in self.rules:
            make_new_rule(rule)

        for rule in rules:
            make_new_rule(rule)

        for index in range(len(matching_rules) - 1):
            if not self.isstronger(matching_rules[index], matching_rules[index + 1]):
                print(f'ambiguous rules while shifting \'{type}\':')
                for name, rule in zip(matching_names, matching_rules):
                    print(f'  {name}: {rule}')
                break

        if len(matching_names) > 0 and not matching_names[0].endswith('?'):
            # This edge will definitely reduce, so there is no need identify a
            # target state for it.
            return None, matching_names[0]

        # This edge may shift more types so a target state must be identified.
        state = self.make_state(new_rules)
        return state, matching_names[0] if len(matching_names) > 0 else None

    def visit_rules(self):
        rules = self.rules_to_visit.pop()
        state = self.state_rules[rules]

        edges = []
        targets = {}
        
        # set of types that appear at this point in the any of the rules.
        types = self.types.union(rule[1][rule[2]] for rule in rules)

        # extend this set with all possible subtypes
        for sup in list(types):
            if sup in self.order:
                types.update(self.order[sup])

        # determine next state for a given type
        for type in types:
            target = self.make_target(rules, type)

            # keep only the most generic type that leads to a state.
            if target not in targets or self.issubtype(targets[target], type):
                targets[target] = type

        # filter out edges that already appear in the base state.
        for target, type in targets.items():
            edge = (type, target[0], target[1])
            if state > 0 and edge in self.states[0]:
                continue
            for index in range(len(edges)):
                entry = edges[index]
                if self.issubtype(type, entry[0]):
                    edges.insert(index, edge)
                    break
            else:
                edges.append(edge)

        self.states[state] = edges

    def build_states(self):
        self.make_state([])

        while len(self.rules_to_visit) > 0:
            self.visit_rules()

    def parse_type_line(self, supertype, subtypes):
        if supertype in self.order:
            self.order[supertype].update(subtypes)
        else:
            self.order[supertype] = set(subtypes)

    def parse_rule_line(self, name, rule):
        self.rules.add((name, tuple(rule), 0))
        self.types.add(rule[0])

    def parse_line(self, line):
        match = re.match(r'\s*(\S+)\s+:>\s+(.+)', line)
        if match is not None:
            return self.parse_type_line(match[1], match[2].split())

        match = re.match(r'\s*(\S+)\s+:\s+(.+)', line)
        if match is not None:
            self.parse_rule_line(match[1], match[2].split())

    def parse(self, filename):
        with open(filename, 'r') as input:
            for line in input:
                self.parse_line(line)

        self.close_order()
        self.build_states()
        return self.states
