
class CompiledBlock:
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes


class CodeBlock(CompiledBlock):
    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_address(address)
        return address


class DataBlock(CompiledBlock):
    def assign_address(self, address):
        for node in self.nodes:
            address = node.assign_word_address(address)
        return address
