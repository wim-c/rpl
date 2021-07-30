
class CompiledBlock:
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes


class CodeBlock(CompiledBlock):
    pass


class DataBlock(CompiledBlock):
    pass
