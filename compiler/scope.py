import tokens

class Scope:
    next_id = 0

    @classmethod
    def get_next_id(cls):
        id = cls.next_id
        cls.next_id += 1
        return id

    def __init__(self, optimizer, parent=None):
        self.id = self.get_next_id()
        self.optimizer = optimizer
        self.parent = parent
        self.symbols = {}
        self.duplicates = set()

    def add_label(self, label):
        mark = label.mark().from_node(label)
        self.try_bind(label.symbol, mark)

    def add_definition(self, definition):
        mark = definition.definition.mark().from_node(definition)
        self.try_bind(definition.symbol, mark)

    def get_mark(self, symbol):
        name = symbol.name
        mark = self.find_name(name)

        if mark is not None:
            return mark

        msg = f'Unresolved symbol \'{name}\''
        self.optimizer.add_error(symbol, msg)

    def try_bind(self, symbol, mark):
        name = symbol.name
        current = self.symbols.get(name)

        if current is None:
            self.symbols[name] = mark
        else:
            self.duplicates.add(name)
            msg = f'Symbol \'{name}\' already defined at l:{current.line}, c:{current.column}'
            self.optimizer.add_error(symbol, msg)

    def find_name(self, name):
        if name in self.duplicates:
            return
        elif name in self.symbols:
            return self.symbols[name]
        elif self.parent is not None:
            return self.parent.find_name(name)
