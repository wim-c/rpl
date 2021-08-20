import argparse
import compiler
import formatter


def dex(txt):
    if txt[0:2] == '0x':
        return int(txt[2:], 16)
    elif txt[0] == '$':
        return int(txt[1:], 16)
    else:
        return int(txt)


parser = argparse.ArgumentParser(description='RPL21 compiler (c) 2021 Wim Couwenberg')
parser.add_argument('-l', '--location', dest='org', metavar='ADDRESS', default=0x401, type=dex, help='The address where the compiled program will be loaded.  Default is 0x401.')
parser.add_argument('-r', '--runtime', dest='rt', metavar='ADDRESS', default=0x9000, type=dex, help='The address where the RPL12 runtime code is located.  Default is 0x9000.')
parser.add_argument('-f', '--format', dest='fmt', default='print', choices=['print', 'basic', 'bin'], help='The format of the generated output.')
parser.add_argument('-o', '--output', dest='output', metavar='FILE', default=None, help='Output will be written to this file path.  Default is stdout.')
parser.add_argument('-p', '--prg', dest='prg', default=False, action='store_true', help='Start the output with a two byte location header.  Has no effect for the output type \'print\'.')
parser.add_argument('file', help='File path of source to compile.')

args = parser.parse_args()

fmt = formatter.Format.create(args.fmt, args.output, args.prg)
cmp = compiler.Compiler()
cmp.compile(args.file, args.org, args.rt, fmt)
