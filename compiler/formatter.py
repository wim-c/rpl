
class PrettyPrinter:
    def __init__(self):
        super().__init__()
        self.emit_empty_line = False
        self.org = None

    def emit(self, address, code, node):
        if self.org is None:
            self.org = address
        byte_code = ' '.join(f'{b:02x}' for b in code[:5])
        print(f'{address:04x} {byte_code:14} {node}')
        for index in range(5, len(code), 5):
            byte_code = ' '.join(f'{b:02x}' for b in code[index:index + 5])
            print(f'{address + index:04x} {byte_code}')
        self.emit_empty_line = True
        return address + len(code)

    def emit_label(self, address, node):
        if self.org is None:
            self.org = address
        if self.emit_empty_line:
            print()
            self.emit_empty_line = False
        print(f'{address:04x} {node}:')
        return address

    def emit_end(self, address):
        if self.org is not None:
            print(f'\norg = ${self.org:04x}\nend = ${address:04x}\n{address - self.org} bytes')
            self.org = None
        self.emit_empty_line = False


class PrgFile:
    def __init__(self, file_name):
        self.file = open(file_name, 'wb')
        self.has_header = False

    def emit(self, address, code, node):
        if not self.has_header:
            self.has_header = True
            header = address.to_bytes(2, 'little')
            self.file.write(header)
        self.file.write(code)
        return address + len(code)

    def emit_label(self, address, node):
        return address

    def emit_end(self, address):
        self.file.close()
        self.file = None
