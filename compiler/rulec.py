import argparse
import rule_compiler as rc
import sys


parser = argparse.ArgumentParser(description='RPL21 rule compiler (c) 2021 Wim Couwenberg')
parser.add_argument('-o', '--output', dest='output', metavar='FILE', default=None, help='Output will be written to this file path.  Default is stdout.')
parser.add_argument('file', help='File path of source to compile.')

args = parser.parse_args()

try:
    builder = rc.StateBuilder()
    builder.parse(args.file)
    text = builder.text()

    if (output := args.output) is None:
        print(text)
    else:
        with open(output, 'w') as f:
            f.write(text)

except Exception as e:
    print(e)
    sys.exit(-1)

