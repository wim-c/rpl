import tokens

class Scope:
    next_id = 0

    @classmethod
    def get_next_id(cls):
        cls.next_id += 1
        return cls.next_id

    def __init__(self, optimizer, parent=None):
        self.id = None
        self.optimizer = optimizer
        self.parent = parent
        self.symbols = {}
        self.duplicates = set()

    def add_label(self, label):
        symbol = label.symbol
        name = self.get_mark_name(symbol.name)
        mark = label.mark(name).from_node(label)
        self.try_bind(symbol, mark)

    def add_definition(self, definition):
        symbol = definition.symbol
        name = self.get_mark_name(symbol.name)
        mark = definition.definition.mark(name).from_node(definition)
        self.try_bind(symbol, mark)

    def get_mark(self, symbol):
        name = symbol.name
        mark = self.find_name(name)

        if mark is not None:
            return mark

        msg = f'Unresolved symbol \'{name}\''
        self.optimizer.add_error(symbol, msg)

    def get_mark_name(self, name):
        if self.parent is None:
            return name
        elif self.id is None:
            self.id = self.get_next_id()
        return f'{name}.{self.id}'

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
