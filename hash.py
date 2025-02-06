import os
import hashlib
import yaml

def file_hash(filename):
    if not os.path.exists(filename):
        return ""

    with open(filename, "r") as file:
        hash = hashlib.md5(file.read().encode())
        return hash.hexdigest()

def update_hash(hashes, filename, parent_filename):
    if filename not in hashes:
        hashes[filename] = {}

    hashes[filename][parent_filename] = file_hash(parent_filename)

def read_hashes(config):
    build_dir = config["build_dir"]
    prefix_dir = config["prefix_dir"]

    if not os.path.isdir(f'{prefix_dir}/{build_dir}'):
        return {}

    if not os.path.isfile(f"{prefix_dir}/{build_dir}/hashes.yaml"):
        return {}

    with open(f"{prefix_dir}/{build_dir}/hashes.yaml", "r") as file:
        hashes = yaml.load(file, Loader=yaml.Loader)

    if hashes == None:
        hashes = {}

    return hashes

def write_hashes(config, hashes):
    build_dir = config["build_dir"]
    prefix_dir = config["prefix_dir"]

    if not os.path.isdir(f'{prefix_dir}/{build_dir}'):
        os.mkdir(f'{prefix_dir}/{build_dir}')

    with open(f"{prefix_dir}/{build_dir}/hashes.yaml", "w") as file:
        file.write(yaml.dump(hashes))

def check_if_file_changed(hashes, filename, parent_filename):
    if (not os.path.exists(filename)) or (filename not in hashes) or (parent_filename not in hashes[filename]):
        return True

    return file_hash(parent_filename) != hashes[filename][parent_filename]
