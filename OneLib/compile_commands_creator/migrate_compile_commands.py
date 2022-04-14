import json
import shutil
import re
from os.path import exists,join, realpath
import os
file_name = 'compile_commands.json'
with open(file_name, 'r') as f:
    data = json.load(f)

cnt = 0

CYBER_DIR = "/home/zhihaohe/cybertron"
PROTO_DIR = '/home/zhihaohe/cybertron'
container_dirs = ['/home/zhihaohe/container_cybertron/usr/local/include/',
                  '/home/zhihaohe/container_cybertron/tmp',
                  '/home/zhihaohe/container_cybertron/usr/include/',
                 '/home/zhihaohe/container_cybertron/pybind11/include/',
                 '/home/zhihaohe/container_cybertron/usr/local/apollo',
                 '/home/zhihaohe/container_cybertron/usr/local/src']

def extract_path_item(path, i):
    path.split('/')[i]

def insert_to_DB(db, fn, path):
    m = db
    items = path.split('/')
    i = -1
    while abs(i) < len(items) and items[i] in db:
        if str is type(db[items[i]]):
            old_path = db[items[i]]
            stem = old_path.split('/')[i]
            assert stem == items[i]
            next_stem = old_path.split('/')[i-1]
            db[items[i]] = {next_stem: old_path}
        else:
            assert dict is type(db[items[i]]), "Bug, should only be str or dict, but it is " + type(db[items[i]])
        db = db[items[i]]
        i -= 1
    if abs(i) >= len(items):
        raise Exception("insert path twice.%s"%path)
    db[items[i]] = path

def build_filepath_db(directory, header_db):
    insert_set = set()
    for fn in os.listdir(directory):
        path = join(directory, fn)
        if path == '/home/zhihaohe/usr_local_cybertron/tmp/lz4-1.9.2/lib/lz4.h':
            print(directory)
        if os.path.isdir(path):
            build_filepath_db(path, header_db)
        elif path not in insert_set:
            insert_set.add(path)
            insert_to_DB(header_db, fn, path)


header_db = {}
for d in container_dirs:
    header_db[d] = {}
    build_filepath_db(d, header_db[d])

with open('header.db', 'w') as f:
    json.dump(header_db, f, indent=2)

def change_file(f, new_dir):
    items = f.split('/')
    a = ''
    for i in items:
        a = i + '/' + a
        if exists(join(new_dir, a)):
            return a
    return None

def search_db(path, db):
    items = path.split('/')
    for i in range(-1, -len(items), -1):
        if items[i] not in db:
            break
        if type(db[items[i]]) is str:
            return db[items[i]]
        assert type(db[items[i]]) is dict
        db = db[items[i]]
    return None

def change_directory(f, d):
    global header_db
    if f.endswith('.pb.h') or f.endswith('.pb.cc'):
        return f, PROTO_DIR
    elif f.endswith('.so') or re.search('so\.\d*', f) or f.endswith('.txx') or f.endswith('.a'):
        # TODO process lib properly
        return f, d
    elif exists(join(CYBER_DIR, f)):
        return f, CYBER_DIR
    else:
        for container_dir, db in header_db.items():
            fp = search_db(f, db)
            if fp:
                assert fp[:len(container_dir)] == container_dir
                return fp[len(container_dir)+1:], container_dir
        return None, None

def migrate_include(cmd, keyword, new_include_path):
    tmpl = '-isystem \S*%s\S*' % keyword
    return re.sub(tmpl, '-isystem %s'%new_include_path, cmd)

def remove_include(cmd, keyword):
    tmpl = '-isystem \S*%s\S*' % keyword
    return re.sub(tmpl, '', cmd)

def insert_include(cmd, path):
    p = cmd.find('-isystem')
    if -1 == p:
        return cmd
    return cmd[:p] + ' -isystem %s '%path + cmd[p:]

def process_command(cmd):
    # remove not used compile flag
    cmd = cmd.replace('-fno-canonical-system-headers', '')
    cmd = insert_include(cmd, '/home/zhihaohe/container_cybertron/usr_local/include')
    cmd = migrate_include(cmd, 'opencv', '/opt/ros/kinetic/include/opencv-3.3.1-dev/')
    cmd = remove_include(cmd, 'boost')
    return cmd

new_data = []
unfound_log = open('./not_founded_files.log', 'w')
for l in data:
    l['command'] = process_command(l['command'])
    # l['directory'] = CYBER_DIR
    f, d = change_directory(l['file'], l['directory'])
    if f and d:
        l['file'] = f
        l['directory'] = d
    else:
        unfound_log.write('%s, %s, %s\n' % (l['directory'], l['file'],
                                            realpath(join(l['directory'],
                                                          l['file']))))
    new_data.append(l)

shutil.move(file_name, file_name + '.backup')
with open('compile_commands.json', 'w') as f:
    json.dump(new_data, f, indent=2)
