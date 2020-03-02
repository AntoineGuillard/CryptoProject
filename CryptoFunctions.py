from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms

# noinspection PyTypeChecker
from SecondaryFunctions import get_file_name


def kdf(key):
    salt = b'e\xd6e\xfcY\x0f|\t\xa3\xd2\x15\xbe\x8a\xa9x\x8c'
    keys = PBKDF2(key, salt, 64, count=1000000, hmac_hash_module=SHA512)
    return keys[19:35]


def padding(bytes_file):
    if len(bytes_file) % AES.block_size == 0:
        return bytes_file
    size = (len(bytes_file) // AES.block_size) + 1
    bytes_file = bytes_file.ljust(AES.block_size * size, b'\0')
    return bytes_file


def cipher_file(key, input_file):
    # Open file in reading binary mode and store it inside a variable
    with open(input_file, 'rb') as fileToCipher:
        new_byte_file = bytearray(fileToCipher.read())
        fileToCipher.close()

    size_of_file = len(new_byte_file)

    # Convert the key to the right format
    bytes_key = bytes.fromhex(key)
    # Create Cipher function
    cipher = AES.new(bytes_key, AES.MODE_ECB)

    if size_of_file % AES.block_size == 0:
        return [input_file] + cipher_func(cipher, new_byte_file)
    return [input_file] + cts_cipher(cipher, new_byte_file)


def cipher_func(cipher_, byte_file):
    # Generate IV
    iv = bytearray(Random.new().read(AES.block_size))
    # Select first block of 16 bytes
    block = byte_file[0:AES.block_size]
    # XOR block with iv
    block_xored = bytearray([_a ^ _b for _a, _b in zip(iv, block)])
    # Cipher the result of the precedent XOR
    block_ciphered = bytearray(cipher_.encrypt(block_xored))
    # Store the result in a variable
    bytes_ciphered = block_ciphered

    # Repeat the process to create CBC operation mode instead of ECB
    for i in range(1, int(len(byte_file) / AES.block_size)):
        block = byte_file[i * AES.block_size:(i + 1) * AES.block_size]
        block_xor = bytearray([_a ^ _b for _a, _b in zip(block_ciphered, block)])
        block_ciphered_next = cipher_.encrypt(block_xor)
        block_ciphered = block_ciphered_next
        bytes_ciphered += block_ciphered
    return [bytes_ciphered, iv]


def cts_cipher(cipher_method, byte_file):
    # CTS Cipher
    # Store the size of the file
    size_of_file = len(byte_file)
    # First part for cipher in cts is the same so we call the function for file which are multiple of 16 bytes
    classic_cipher = cipher_func(cipher_method, padding(byte_file))
    bytes_ciphered = classic_cipher[0]

    # 1 We store the "n-1" block in a variable
    block_before_cut = bytes_ciphered[-(AES.block_size * 2):-AES.block_size]
    # 2 Cut to the required size
    block_after_cut = block_before_cut[0:-(AES.block_size - size_of_file % AES.block_size)]
    # 3 This one is the new n-1 block
    before_last = bytes_ciphered[-AES.block_size:]

    # The n and n-1 ciphered bytes are removed to be replaced
    bytes_ciphered = bytes_ciphered[0:-AES.block_size * 2]

    # Adding the new n-1 block
    bytes_ciphered += before_last
    # Adding the new n block
    bytes_ciphered += block_after_cut
    return_value = [bytes_ciphered, classic_cipher[1]]
    return return_value


def decipher_file(key, input_file, iv, json_dict):
    # Generate IV
    with open(input_file, 'rb') as file_to_decipher:
        byte_file_ciphered = bytearray(file_to_decipher.read())
        file_to_decipher.close()
    if cmac(key, byte_file_ciphered) != bytearray(
            [int(i) for i in json_dict[get_file_name(input_file[0:-4]) + ".mac"].strip('][').split(', ')]):
        print("The file has been altered\nNow Exiting")
        exit()
    else:
        print("The integrity of the file has been verified")

    size_of_file = len(byte_file_ciphered)

    bytes_key = bytes.fromhex(key)
    decipher = AES.new(bytes_key, AES.MODE_ECB)
    # Ciphered Block
    block = bytearray(byte_file_ciphered[0:AES.block_size])
    # Deciphered Before XOR
    block_ciphered_next = bytearray(decipher.decrypt(block))
    # Block Completely Deciphered
    block_xor = bytearray([_a ^ _b for _a, _b in zip(iv, block_ciphered_next)])

    bytes_deciphered = block_xor

    if size_of_file % AES.block_size == 0:
        # Iterative to decipher the whole file
        bytes_deciphered += decipher_simple(decipher, byte_file_ciphered, block)
        return [input_file] + [bytes_deciphered]

    else:
        bytes_deciphered += cts_decipher(decipher, byte_file_ciphered, block)
        # Remove the unnecessary padding at the end of the file
        bytes_deciphered = bytes_deciphered[0:size_of_file]
        return [input_file] + [bytes_deciphered]


def decipher_simple(decipher, byte_file_ciphered, block):
    bytes_deciphered = bytearray()
    for i in range(1, int(len(byte_file_ciphered) / AES.block_size) - 1):
        # Current Ciphered Block
        current_block = byte_file_ciphered[i * AES.block_size:(i + 1) * AES.block_size]
        # Decipher current block
        block_deciphered = decipher.decrypt(current_block)
        block_xor = bytearray([_a ^ _b for _a, _b in zip(block_deciphered, block)])
        block = current_block
        bytes_deciphered += block_xor

    return bytes_deciphered


def cts_decipher(decipher, byte_file_ciphered, block_):
    # Initialize variable to later store the n-2 block cipher text to xor with the n-1 block
    to_xor_later = 0
    size_of_file = len(byte_file_ciphered)
    bytes_deciphered = bytearray()

    for i in range(1, len(byte_file_ciphered) // AES.block_size - 1):
        # Current Ciphered Block
        current_block = byte_file_ciphered[i * AES.block_size:(i + 1) * AES.block_size]
        # Decipher current block

        # Store the cipher text for later
        if i == int(len(byte_file_ciphered) / AES.block_size) - 2:
            to_xor_later = current_block

        if i < int(len(byte_file_ciphered) / AES.block_size) - 1:
            # Decipher block
            block_deciphered = decipher.decrypt(current_block)
            # XOR with previous ciphered block
            block_xor = bytearray([_a ^ _b for _a, _b in zip(block_deciphered, block_)])
            # Store current block to XOR with it at the next iteration
            block_ = current_block
            # Add to the global deciphered
            bytes_deciphered += block_xor

    # Get the last part of the ciphered file
    byte_file_ciphered = byte_file_ciphered[-(size_of_file % AES.block_size + AES.block_size):]

    # 1 Create the block of 16 bytes n-1
    block_ = byte_file_ciphered[0:AES.block_size]

    # 2 Decipher the block
    block_ = decipher.decrypt(block_)

    # 3 Get last block of the ciphered file
    last_block = byte_file_ciphered[AES.block_size:]

    # 4 Store the end of the block
    end_of_block = block_[-(AES.block_size - len(last_block)):]

    # 5 Create n-1 block with last bytes of the ciphered file and the end of the n-1 block to get a 16 bytes block
    before_last = last_block + bytearray(end_of_block)

    # 6 Decipher the newly created n-1 block
    before_last_deciphered = decipher.decrypt(before_last)

    # 7 XOR with the variable we stored earlier to get the "plain bytes" of the file
    before_last_plain = bytearray([_a ^ _b for _a, _b in zip(to_xor_later, before_last_deciphered)])

    # 8 XOR with n-1 ciphered bytes to get the last clear bytes
    last = bytearray([_a ^ _b for _a, _b in zip(before_last, block_)])

    # Add n-1 block to deciphered bytearray
    bytes_deciphered += before_last_plain
    # Add n block to deciphered bytearray
    bytes_deciphered += last
    return bytes_deciphered


def cmac(key, ciphered_bytes):
    # Transform key into binary format
    bytes_key = bytes.fromhex(key)
    # Derive the key to not use the same for encryption and integrity
    derived_key = kdf(bytes_key)
    c = cmac.CMAC(algorithms.AES(derived_key), backend=default_backend())
    c.update(bytes(ciphered_bytes))
    return c.finalize()



