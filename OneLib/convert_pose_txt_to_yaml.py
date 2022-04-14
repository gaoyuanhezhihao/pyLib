import yaml
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("directory")
args = parser.parse_args()

pose_filenames = [name for name in os.listdir(args.directory) if name.endswith('.txt')]

def ReadPose(lines):

for filename in pose_filenames:
    with open(os.path.join(args.directory, filename), 'r') as f:
        lines = f.readlines()

print(yaml.dump({'eskf':{'translation':a} }))
