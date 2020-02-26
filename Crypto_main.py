import json
import os
import shutil
import sys
from pathlib import Path
from CryptoProject import *

inputs = sys.argv


def check_inputs(arguments):
    size_of_command = len(arguments)
    # Check if the command as the minimum arguments needed
    if size_of_command < 8:
        print(
            "Please enter the right number of arguments.\nThe Command as to be like this: filecrypt –enc|-dec –key "
            "F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Verify if the first argument is -enc of -dec
    if arguments[1] != "-enc" and arguments[1] != "-dec":
        print(arguments[1])
        print(
            "You must choose if you want to encrypt or decrytp file(s).\nThe Command as to be like this: filecrypt "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Verify the option -key is present
    if arguments[2] != "-key":
        print(
            "You must enter the -key option followed by a password of 128 bits in hexadecimal.\nThe Command as to be "
            "like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Check if the key is hexadecimal and his size is 128 bits
    if len(arguments[3]) != 32 or is_not_hex(arguments[3]):
        print(
            "You must enter a key of 32 charater in hexadecimal.\nThe Command as to be like this: filecrypt –enc|-dec "
            "–key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Check for the option -in
    if arguments[4] != "-in":
        print(
            "You must enter the -in option to take files as input.\nThe Command as to be like this: filecrypt "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Check for the option -out
    if arguments[size_of_command - 2] != "-out":
        print(
            "You must enter the -out option to take files as output.\nThe Command as to be like this: filecrypt "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    # Check if zipped file already exist and ask the user if he want to remove it
    if file_exist(arguments[size_of_command - 1] + ".zip"):
        answer = ""
        while answer != "yes" and answer != "no":
            answer = input("The file you put as output file already exist do you want to overwrite it ?(yes/no)")
        if answer == "yes":
            os.remove(arguments[- 1] + ".zip")
        else:
            print("If you don't want to delete the existing file please enter a different name")
            exit()
    # We'll need the name to create a temporary directory so we check if it exist first
    if os.path.isdir(arguments[- 1]):
        print("Please enter another name for the output file")
    # Verify if the file(s) in input exists
    for i in range(5, size_of_command - 2):
        if not file_exist(arguments[i]):
            print(
                "The files you enter to cipher or decipher must exists.\nThe Command as to be like this: filecrypt "
                "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
            print("There is at least one error for the " + str(i - 4) + "st/nd/th file")
            exit()
        else:
            print("The file already exist")
    if arguments[1] == "-enc":
        return True
    else:
        return False


def create_zip(zip_file_name, files):
    # Try to Create Directory to zip all the file together
    try:
        os.mkdir(zip_file_name, 0o755)
    except OSError:
        print("Creation of the directory %s failed" % zip_file_name)
        exit()
    else:
        print("Successfully created the directory %s" % zip_file_name)

    if len(files[0]) == 2:
        # Iterate in an array of type {[filePath1, bytes of ciphered File1,iv],...}
        for file_resources in files:
            # Crate file inside the newly created directory
            with open(zip_file_name + "/" + get_file_name(file_resources[0][0:-4]), 'wb') as file_deciphered:
                file_deciphered.write(file_resources[1])
                file_deciphered.close()

    elif len(files[0]) == 3:
        dict_for_json = {}
        if file_exist(get_dir_name(zip_file_name) + "/iv.json"):
            with open(get_dir_name(zip_file_name) + "/iv.json", 'rb') as jsonFile:
                dict_for_json = json.loads(jsonFile.read())
                jsonFile.close()

        for file_resources in files:
            # Create file inside the newly created directory
            with open(zip_file_name + "/" + get_file_name(file_resources[0]) + ".enc", 'wb') as fileCiphered:
                fileCiphered.write(file_resources[1])
                fileCiphered.close()

            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            print(file_resources[2])
            dict_for_json[get_file_name(file_resources[0])] = str(list(file_resources[2]))
        # Write the new content of IVs in the json file
        with open(zip_file_name + "/iv.json", 'w') as json_file:
            json_file.write(json.dumps(dict_for_json))
            json_file.close()
    # ZIP the directory
    shutil.make_archive(zip_file_name, 'zip', zip_file_name)
    # Remove the directory
    shutil.rmtree(zip_file_name)


def main(arguments):
    # check_inputs(arguments) UT needed for check if zip exist and check if directory exist
    encrypt = check_inputs(arguments)
    create_zip(arguments[-1], array_files(arguments[3], arguments[5: len(arguments) - 2], encrypt))
    pass


if __name__ == "__main__":
    main(inputs)
