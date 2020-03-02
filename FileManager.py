import json
import os
import shutil

from CryptoFunctions import cipher_file, cmac, decipher_file
from SecondaryFunctions import get_dir_name, get_file_name, is_not_hex, file_or_directory_exist


def check_inputs(arguments):
    size_of_command = len(arguments)
    # Check if the command as the minimum arguments needed
    if size_of_command < 8:
        print(
            "Please enter the right number of arguments.\nThe Command as to be like this: python3 Crypto_main.py –enc|-dec –key "
            "F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Verify if the first argument is -enc of -dec
    if arguments[1] != "-enc" and arguments[1] != "-dec":
        print(arguments[1])
        print(
            "You must choose if you want to encrypt or decrytp file(s).\nThe Command as to be like this: python3 Crypto_main.py "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Verify the option -key is present
    if arguments[2] != "-key":
        print(
            "You must enter the -key option followed by a password of 128 bits in hexadecimal.\nThe Command as to be "
            "like this: python3 Crypto_main.py –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Check if the key is hexadecimal and his size is 128 bits
    if len(arguments[3]) != 32 or is_not_hex(arguments[3]):
        print(
            "You must enter a key of 32 charater in hexadecimal.\nThe Command as to be like this: python3 Crypto_main.py –enc|-dec "
            "–key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Check for the option -in
    if arguments[4] != "-in":
        print(
            "You must enter the -in option to take files as input.\nThe Command as to be like this: python3 Crypto_main.py "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Check for the option -out
    if arguments[size_of_command - 2] != "-out":
        print(
            "You must enter the -out option to take files as output.\nThe Command as to be like this: python3 Crypto_main.py "
            "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
        exit()
    # Check if zipped file already exist and ask the user if he want to remove it
    if file_or_directory_exist(arguments[size_of_command - 1] + ".zip"):
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
        if not file_or_directory_exist(arguments[i]):
            print(
                "The files you enter to cipher or decipher must exists.\nThe Command as to be like this: python3 Crypto_main.py "
                "–enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>\nAnd there is no need to put a '.zip' at the end of the output file")
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
    if file_or_directory_exist(zip_file_name):
        answer = ""
        while answer != "yes" and answer != "no":
            answer = input("This name is needed to create a temporary directory, do you want to delete it anyway (yes/no)")
        if answer == "yes":
            shutil.rmtree(zip_file_name)
        else:
            print("You must enter a different name of file for your zip file ")
    try:
        os.mkdir(zip_file_name, 0o755)
    except OSError:
        print("Creation of the directory %s failed" % zip_file_name)
        exit()

    if len(files[0]) == 2:
        # Iterate in an array of type {[filePath1, bytes of ciphered File1,iv],...}
        for file_resources in files:
            # Create file inside the newly created directory
            with open(zip_file_name + "/" + get_file_name(file_resources[0][0:-4]), 'wb') as file_deciphered:
                file_deciphered.write(file_resources[1])
                file_deciphered.close()

    elif len(files[0]) == 3:
        dict_for_json = files.pop()
        if file_or_directory_exist(get_dir_name(zip_file_name) + "/iv.json"):
            with open(get_dir_name(zip_file_name) + "/iv.json", 'rb') as jsonFile:
                dict_for_json = json.loads(jsonFile.read())
                jsonFile.close()

        for file_resources in files:
            # Create file inside the newly created directory
            with open(zip_file_name + "/" + get_file_name(file_resources[0]) + ".enc", 'wb') as fileCiphered:
                fileCiphered.write(file_resources[1])
                fileCiphered.close()

            dict_for_json[get_file_name(file_resources[0])] = str(list(file_resources[2]))
        # Write the new content of IVs in the json file
        with open(zip_file_name + "/iv.json", 'w') as json_file:
            json_file.write(json.dumps(dict_for_json))
            json_file.close()
    # ZIP the directory
    shutil.make_archive(zip_file_name, 'zip', zip_file_name)
    # Remove the directory
    shutil.rmtree(zip_file_name)
    return 0


# Create an array of lists, the last file is filled with name of input file, byte_array ciphered or decipher file, and iv
def array_files(key, input_files, encrypt):
    list_of_ciphered = []
    # Encrypt all files in input
    if encrypt:
        json_dict = {}
        if file_or_directory_exist(get_dir_name(input_files[0]) + "/iv.json"):
            with open(get_dir_name(input_files[0]) + "/iv.json", 'r') as jsonFile:
                json_dict = json.loads(jsonFile.read())

        for i, fileToCipher in enumerate(input_files):
            list_of_ciphered.append(cipher_file(key, fileToCipher))
            json_dict[get_file_name(fileToCipher) + ".mac"] = str(list(cmac(key, list_of_ciphered[i][1])))
        list_of_ciphered.append(json_dict)
        return list_of_ciphered
    # Decrypt all files in input thanks to the iv stored in a json file
    else:
        # Open json of IV if it exist
        json_dict = {}
        if file_or_directory_exist(get_dir_name(input_files[0]) + "/iv.json"):
            with open(get_dir_name(input_files[0]) + "/iv.json", 'r') as jsonFile:
                json_dict = json.loads(jsonFile.read())
        else:
            print("The files to decrypt must be in the same directory as the iv.json file")
            exit()
        list_of_deciphered = []
        for fileToDecipher in input_files:
            list_of_deciphered.append(decipher_file(key, fileToDecipher, bytearray(
                [int(i) for i in json_dict[get_file_name(fileToDecipher[0:-4])].strip('][').split(', ')]), json_dict))

        return list_of_deciphered
