
class PrettyPrinter:
    def __init__(self):
        super().__init__()
        self.emit_empty_line = False

    def emit(self, address, code, node):
        byte_code = ' '.join(f'{b:02x}' for b in code[:5])
        print(f'{address:04x} {byte_code:14} {node}')
        for index in range(5, len(code), 5):
            byte_code = ' '.join(f'{b:02x}' for b in code[index:index + 5])
            print(f'{address + index:04x} {byte_code}')
        self.emit_empty_line = True
        return address + len(code)

    def emit_label(self, address, node):
        if self.emit_empty_line:
            print()
            self.emit_empty_line = False
        print(f'{address:04x} {node}:')
        return address
