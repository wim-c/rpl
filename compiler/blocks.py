
import tokens


class CompiledBlock:
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes
        self.reachable = False

        for index, node in enumerate(self.nodes):
            if isinstance(node, tokens.Mark):
                node.set_block_index(self, index)

    def set_visited_from_index(self, start, marks_to_visit):
        self.reachable = True
        for index in range(start, len(self.nodes)):
            if not self.nodes[index].set_visited(marks_to_visit):
                break


class CodeBlock(CompiledBlock):
    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_address(address)
        return address

    def visit(self):
        marks_to_visit = set()
        self.set_visited_from_index(0, marks_to_visit)

        while len(marks_to_visit) > 0:
            marks_to_visit.pop().visit(marks_to_visit)

    def emit(self, address, formatter):
        for node in self.nodes:
            address = node.emit(address, formatter)
        return address


class DataBlock(CompiledBlock):
    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_word_address(address)
        return address

    def set_visited_from_index(self, start, marks_to_visit):
        super().set_visited_from_index(0, marks_to_visit)

    def emit(self, address, formatter):
        for node in self.nodes:
            address = node.emit_word(address, formatter)
        return address
