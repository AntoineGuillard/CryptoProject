import os
from pathlib import Path


# Check if it is hexadecimal for the key
def is_not_hex(s):
    try:
        int(s, 16)
        return False
    except ValueError:
        return True


# Check if the file exist
def file_or_directory_exist(file_path):
    if Path(file_path).exists():
        return True
    else:
        return False


def directory_exist(path):
    if Path(path).is_dir():
        return True
    else:
        return False


def get_file_name(absolute_path):
    if not os.path.isabs(absolute_path):
        return absolute_path
    # Allow to get the filename without the absolute path
    absolute_path = absolute_path[::-1]
    file_name = ""
    i = 0
    while absolute_path[i] != "/":
        file_name += absolute_path[i]
        i += 1
    return file_name[::-1]


def get_dir_name(path):
    if not os.path.isabs(path):
        return path
    path = path[::-1]
    i = 0
    while path[i] != "/":
        i += 1
    dir_name = path[i:]
    return dir_name[::-1]
