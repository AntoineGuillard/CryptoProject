from Crypto.Cipher import AES
from Crypto import Random
from Crypto_main import *


# Check if it is hexadecimal for the key
def is_not_hex(s):
    try:
        int(s, 16)
        return False
    except ValueError:
        return True


# Check if the file exist
def file_exist(file_path):
    if Path(file_path).is_file():
        return True
    else:
        return False


def get_file_name(absolute_path):
    # Allow to get the filename without the absolute path
    absolute_path = absolute_path[::-1]
    file_name = ""
    i = 0
    while absolute_path[i] != "/":
        file_name += absolute_path[i]
        i += 1
    return file_name[::-1]


def get_dir_name(path):
    path = path[::-1]
    i = 0
    while path[i] != "/":
        i += 1
    dir_name = path[i:]
    return dir_name[::-1]


def cipher_file(key, input_file):
    # Generate IV
    iv = bytearray(Random.new().read(AES.block_size))
    # Open file in reading binary mode and store it inside a variable
    with open(input_file, 'rb') as fileToCipher:
        new_byte_file = bytearray(fileToCipher.read())
        fileToCipher.close()

    # Convert the key to the right format
    bytes_key = bytes.fromhex(key)
    # Create Cipher function
    cipher = AES.new(bytes_key, AES.MODE_ECB)
    # Select first block of 16 bytes
    block = new_byte_file[0:AES.block_size]
    # XOR block with iv
    block_xored = bytearray([_a ^ _b for _a, _b in zip(iv, block)])
    # Cipher the result of the precedent XOR
    block_ciphered = bytearray(cipher.encrypt(block_xored))
    # Store the result in a variable
    bytes_ciphered = block_ciphered

    # Repeat the process to create CBC operation mode instead of ECB
    for i in range(1, int(len(new_byte_file) / AES.block_size)):
        block = new_byte_file[i * AES.block_size:(i + 1) * AES.block_size]
        block_xor = bytearray([_a ^ _b for _a, _b in zip(block_ciphered, block)])
        block_ciphered_next = cipher.encrypt(block_xor)
        block_ciphered = block_ciphered_next
        bytes_ciphered += block_ciphered

    return [input_file, bytes_ciphered, iv]


def decipher_file(key, input_file, iv):
    # Generate IV

    with open(input_file, 'rb') as file_to_decipher:
        byte_file_ciphered = bytearray(file_to_decipher.read())
        file_to_decipher.close()
    bytes_key = bytes.fromhex(key)
    decipher = AES.new(bytes_key, AES.MODE_ECB)
    # Ciphered Block
    block = bytearray(byte_file_ciphered[0:AES.block_size])
    # Deciphered Before XOR
    block_ciphered_next = bytearray(decipher.decrypt(block))
    # Block Completely Deciphered
    block_xor = bytearray([_a ^ _b for _a, _b in zip(iv, block_ciphered_next)])

    bytes_deciphered = block_xor

    # Iterative to decipher the whole file
    for i in range(1, int(len(byte_file_ciphered) / AES.block_size)):
        # Current Ciphered Block
        current_block = byte_file_ciphered[i * AES.block_size:(i + 1) * AES.block_size]
        # Decipher current block
        block_deciphered = decipher.decrypt(current_block)
        # XOR result with old ciphered Block
        block_xor = bytearray([_a ^ _b for _a, _b in zip(block_deciphered, block)])
        block = current_block
        # Add Deciphered Block to Byte_array
        bytes_deciphered += block_xor
    print("File deciphered in decipher file")
    print(bytes_deciphered)
    print(bytes_deciphered)
    print(bytes_deciphered)
    print(bytes_deciphered)
    print(bytes_deciphered)
    return [input_file, bytes_deciphered]


# Create an array of lists, the last file is filled with name of input file, byte_array ciphered or decipher file, and iv
def array_files(key, input_files, encrypt):
    list_of_ciphered = []
    # Encrypt all files in input
    if encrypt:
        for fileToCipher in input_files:
            list_of_ciphered.append(cipher_file(key, fileToCipher))
        print(list_of_ciphered)
        return list_of_ciphered
    # Decrypt all files in input thanks to the iv stored in a json file
    else:
        # Open json of IV if it exist
        json_dict = {}
        if file_exist(get_dir_name(input_files[0]) + "/iv.json"):
            with open(get_dir_name(input_files[0]) + "/iv.json", 'r') as jsonFile:
                json_dict = json.loads(jsonFile.read())
        else:
            print("The files to decrypt must be in the same directory as the iv.json file")
            exit()
        list_of_deciphered = []
        for fileToDecipher in input_files:
            list_of_deciphered.append(decipher_file(key, fileToDecipher, bytearray(
                [int(i) for i in json_dict[get_file_name(fileToDecipher[0:-4])].strip('][').split(', ')])))
        return list_of_deciphered


