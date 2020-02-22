from Crypto.Cipher import AES
from Crypto import Random
from Crypto_main import *



key = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"

def cipherFile(key,inputFile):
    #Generate IV
    iv = Random.new().read(AES.block_size)
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
    for i in range(1,int(len(newByteFile)/AES.block_size)):
        block = newByteFile[i*AES.block_size:(i+1)*AES.block_size]
        blockXOR = bytearray([_a ^ _b for _a, _b in zip(blockciphered, block)])
        blockcipheredNext = cipher.encrypt(blockXOR)
        blockciphered = blockcipheredNext
        bytesCiphered += blockciphered
    
    return [inputFile,blockciphered,iv]

    
def decipher(key,inputFile,iv):
    #Generate IV
    iv = Random.new().read(AES.block_size)
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
    for i in range(1,int(len(byteFileCiphered)/AES.block_size)):
        #Current Ciphered Block
        currentBlock = byteFileCiphered[i*AES.block_size:(i+1)*AES.block_size]
        #Decipher current block
        blockDeciphered = decipher.decrypt(currentBlock)
        #XOR result with old ciphered Block
        blockXOR = bytearray([_a ^ _b for _a, _b in zip(blockDeciphered, block)])
        block = currentBlock
        #Add Deciphered Block to Bytearray
        bytesDeciphered += blockXOR
    
    return [inputFile,bytesDeciphered]



#Create an array of lists, the last file is filled with name of input file, bytearray ciphered or decipher file, and iv
def arrayFiles(key,inputfiles,encrypt):
    #Encrypt all files in input
    if encrypt:
        for fileToCipher in inputfiles:
            listofCiphered += cipherFile(key,fileToCipher)
        return listofCiphered
    #Decrypt all files in input thanks to the iv stored in a json file
    else:
        #Open json of IV if it exist
        if fileExist(getDirName(inputfiles)+"/iv.json"):
            with open(getDirName(inputfiles)+"/iv.json",'rb') as jsonFile:
                json_dict = json.loads(jsonFile.read())
        else:
            print("The files to decrypt must be in the same directory as the iv.json file")
            exit()
        for fileToDecipher in inputfiles:
            listOfDeciphered += decipher(key,fileToCipher,json_dict[getFileName(fileToDecipher)])
        return listOfDeciphered



############################################################
##
#NEED TO TEST SUPPLY CHAIN BETWEEN CIPHER/DECIPHER ARRAYFILES and CREATEZIP#
##
############################################################