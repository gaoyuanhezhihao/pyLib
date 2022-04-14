import json
import shutil
import re
from os.path import exists,join
file_name = 'compile_commands.json'
with open(file_name, 'r') as f:
    data = json.load(f)

directory_set = set()


for l in data:
    # if 'fastcdr' in l['file'] :
        # print(l['file'])
        # print(l['directory'])
    if 'edline_pole2d_feature_extractor' in l['file']:
        print(l['file'])
        print(l['directory'])
        print(l['command'])
    path = join(l['directory'], l['file'])
    # if 'semantic_localization_config' in l['file']:
        # print(l['file'])
        # print(l['directory'])
        # print(l['command'])

    # directory_set.add(l['directory'])
# print(directory_set)
