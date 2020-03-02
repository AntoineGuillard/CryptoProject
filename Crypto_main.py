#!/usr/bin/python3
import sys

from FileManager import create_zip, array_files, check_inputs

inputs = sys.argv


def main(arguments):
    encrypt = check_inputs(arguments)
    create_zip(arguments[-1], array_files(arguments[3], arguments[5: len(arguments) - 2], encrypt))
    return 0


if __name__ == "__main__":
    main(inputs)
