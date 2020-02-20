from Crypto.Cipher import AES
from Crypto import Random

# inputFile '/Users/antoine/Dev/CryptoProject/test1.txt'
# outputFile '/Users/antoine/Dev/CryptoProject/result.txt'

iv = Random.new().read(AES.block_size)
key = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"

def cipherFile(key,inputFile,outputFile,iv):
    #Open file in reading binary mode and store it inside a variable
    with open(inputFile, 'rb') as fileToCipher:
        newByteFile = bytearray(fileToCipher.read())
        fileToCipher.close()
    #Convert the key to the right format
    bytesKey = bytes.fromhex(key)
    #Create Cipher function
    cipher = AES.new(bytesKey, AES.MODE_ECB)
    # Select first block of 16 bytes
    block = newByteFile[0:AES.block_size]
    #XOR block with iv
    blockXORed = bytearray([_a ^ _b for _a, _b in zip(iv, block)])
    #Cipher the result of the precedent XOR
    blockciphered = bytearray(cipher.encrypt(blockXORed))
    #Store the result in a variable
    bytesCiphered = blockciphered

    #Repeat the process to create CBC operation mode instead of ECB
    for i in range(1,int(len(newByteFile)/AES.block_size)-1):
        block = newByteFile[i*AES.block_size:(i+1)*AES.block_size]
        blockXOR = bytearray([_a ^ _b for _a, _b in zip(blockciphered, block)])
        blockcipheredNext = cipher.encrypt(blockXOR)
        blockciphered = blockcipheredNext
        bytesCiphered += blockciphered
    with open(outputFile, 'wb') as fileCiphered:
        fileCiphered.write(bytesCiphered)
        del bytesCiphered
        fileCiphered.close()
    
def decipher(key,inputFile,outputFile,iv):
    with open(inputFile, 'rb') as fileCiphered:
        byteFileCiphered = bytearray(fileCiphered.read())
        fileCiphered.close()
    bytesKey = bytes.fromhex(key)
    decipher = AES.new(bytesKey, AES.MODE_ECB)
    #Ciphered Block
    block = bytearray(byteFileCiphered[0:AES.block_size])
    #Deciphered Before XOR
    blockcipheredNext = bytearray(decipher.decrypt(block))
    #Block Completely Deciphered
    blockXOR = bytearray([_a ^ _b for _a, _b in zip(iv, blockcipheredNext)])
    
    bytesDeciphered = blockXOR

    #Iterative to decipher the whole file
    for i in range(1,int(len(byteFileCiphered)/AES.block_size)-1):
        #Current Ciphered Block
        currentBlock = byteFileCiphered[i*AES.block_size:(i+1)*AES.block_size]
        #Decipher current block
        blockDeciphered = decipher.decrypt(currentBlock)
        #XOR result with old ciphered Block
        blockXOR = bytearray([_a ^ _b for _a, _b in zip(blockDeciphered, block)])
        block = currentBlock
        #Add Deciphered Block to Bytearray
        bytesDeciphered += blockXOR
    
    with open(outputFile, 'wb') as fileCiphered:
        fileCiphered.write(bytesDeciphered)
        del bytesDeciphered
        fileCiphered.close()








