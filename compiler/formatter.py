import sys

class Format:
    @classmethod
    def create(cls, fmt, output, prg):
        if fmt == 'print':
            return PrintFormat(output, prg)
        elif fmt == 'basic':
            return BasicFormat(output, prg)
        elif fmt == 'bin':
            return BinFormat(output, prg)

    def __init__(self, output, prg):
        self.output = output
        self.prg = prg

    def open_text(self):
        if self.output is None:
            self.stream = sys.stdout
        else:
            self.stream = open(self.output, 'w')

    def open_binary(self, org):
        self.stream = open(self.output, 'wb')

        if self.prg:
            header = org.to_bytes(2, 'little')
            self.stream.write(header)

    def close(self):
        self.stream.close()
        self.stream = None


class PrintFormat(Format):
    def __init__(self, output, prg):
        super().__init__(output, prg)
        self.emit_empty_line = False

    def emit_begin(self, org):
        self.open_text()
        return org

    def emit(self, address, code, node):
        byte_code = ' '.join(f'{b:02x}' for b in code[:5])
        self.stream.write(f'{address:04x} {byte_code:14} {node}\n')
        for index in range(5, len(code), 5):
            byte_code = ' '.join(f'{b:02x}' for b in code[index:index + 5])
            self.stream.write(f'{address + index:04x} {byte_code}\n')
        self.emit_empty_line = True
        return address + len(code)

    def emit_label(self, address, node):
        if self.emit_empty_line:
            self.stream.write('\n')
            self.emit_empty_line = False
        self.stream.write(f'{address:04x} {node}:\n')
        return address

    def emit_end(self, org, address):
        self.stream.write(f'\norg = ${org:04x}\nend = ${address:04x}\n{address - org} bytes\n')
        self.close()


class BinFormat(Format):
    def emit_begin(self, org):
        self.open_binary(org)
        return org

    def emit(self, address, code, node):
        self.stream.write(code)
        return address + len(code)

    def emit_label(self, address, node):
        return address

    def emit_end(self, org, address):
        self.close()


class BasicFormat(BinFormat):
    def emit_begin(self, org):
        super().emit_begin(org)

        size = 9
        while (nsize := 9 + len(str(org + size))) != size:
            size = nsize

        address = org + size
        basic = (address - 2).to_bytes(2, 'little') + b'\x0a\x00\x9e\x20' + str(address).encode('latin-1') + b'\x00\x00\x00'
        self.stream.write(basic)
        return address
