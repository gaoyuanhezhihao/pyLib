import argparse
from datetime import datetime

def strip_timestamp(line):
    first_whitespace = line.find(' ')
    timestamp = line[:first_whitespace]
    # print(timestamp)
    return datetime.strptime(timestamp, '%H:%M:%S.%f'), line[first_whitespace:]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('log_path')
    args = p.parse_args()
    with open(args.log_path, 'r') as f:
        lines = f.readlines()
    start_timestamp, _ = strip_timestamp(lines[0])
    new_lines = []
    for l in lines:
        if len(l) < 10:
            continue
        timestamp, rest = strip_timestamp(l)
        new_l = '%f %s' % ((timestamp - start_timestamp).total_seconds(), rest)
        new_lines.append(new_l)
    with open(args.log_path.replace('log', 'relative_timed.log'), 'w') as f:
        f.write(''.join(new_lines))

