import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file_path', type=str)
parser.add_argument('--comment', default=False, action='store_true',
                    help='comment or uncomment')

args = parser.parse_args()

block_start = '/* vvv debug vvv */'

block_stop = '/* ^^^ debug ^^^ */'

def comment(line):
    return '//' + line

def uncomment(line):
    if len(line) ==0:
        return line
    i = 0
    while i < len(line) and line[i] == '/':
        i += 1
    return line[i:]

print('comment debug blocks' if args.comment else 'uncomment debug blocks')
fp = args.file_path
with open(fp, 'r') as f:
    lines = f.readlines()
    size = len(lines)
    starts = list(filter(lambda i: block_start in lines[i], range(size)))
    ends = list(filter(lambda i: block_stop in lines[i], range(size)))
    if len(starts) != len(ends):
        raise "Error, not equal numbers of starts and stops"
    for start, end in zip(starts, ends):
        for i in range(start+1, end):
            if args.comment:
                lines[i] = '//' + lines[i]
            else:
                lines[i] = uncomment(lines[i])

with open(fp, 'w') as f:
    f.write(''.join(lines))
