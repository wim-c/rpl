
import tokens

class CompiledBlock:
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes
        self.reachable = False

        for index, node in enumerate(self.nodes):
            if isinstance(node, tokens.Mark):
                node.block = self
                node.index = index

    def set_reachable_from_index(self, start, marks_to_visit):
        for index in range(start, len(self.nodes)):
            if not self.nodes[index].set_reachable(marks_to_visit):
                break


class CodeBlock(CompiledBlock):
    def __init__(self, nodes):
        super().__init__(nodes)
        self.first_reachable_index = None

    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_address(address)
        return address

    def set_reachable_from_index(self, start, marks_to_visit):
        if self.reachable:
            self.first_reachable_index = min(self.first_reachable_index, start)
        else:
            self.reachable = True
            self.first_reachable_index = start
        super().set_reachable_from_index(start, marks_to_visit)

    def visit(self):
        marks_to_visit = set()
        self.set_reachable_from_index(0, marks_to_visit)

        while len(marks_to_visit) > 0:
            marks_to_visit.pop().set_used(marks_to_visit)


class DataBlock(CompiledBlock):
    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_word_address(address)
        return address

    def set_reachable_from_index(self, start, marks_to_visit):
        if not self.reachable:
            self.reachable = True
            super().set_reachable_from_index(0, marks_to_visit)
