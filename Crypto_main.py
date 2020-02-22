import sys
import re
from pathlib import Path
import os
import shutil
import json 
import CryptoProject
arguments = sys.argv


#Check if it is hexadecimal for the key
def is_not_hex(s):
    try:
        int(s, 16)
        return False
    except ValueError:
        return True

#Check if the file exist
def fileExist(filePath):
    if Path(filePath).is_file():
        print("exist")
        return True
    else:
        print("NoExist")
        return False
  

    
def checkInputs(arguments):
    sizeOfCommand = len(arguments)
    #Check if the command as the minimum arguments needed
    if sizeOfCommand < 8:
        print("Please enter the right number of arguments.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Verify if the first argument is -enc of -dec
    if arguments[1] != "-enc" and arguments[1] != "-dec":
        print(arguments[1])
        print("You must choose if you want to encrypt or decrytp file(s).\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Verify the option -key is present
    if arguments[2] != "-key":
        print("You must enter the -key option followed by a password of 128 bits in hexadecimal.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Check if the key is hexadecimal and his size is 128 bits
    if len(arguments[3]) != 32 or is_not_hex(arguments[3]):
        print("You must enter a key of 32 charater in hexadecimal.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Check for the option -in
    if arguments[4] != "-in":
        print("You must enter the -in option to take files as input.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Check for the option -out
    if arguments[sizeOfCommand-2] != "-out":
        print("You must enter the -out option to take files as output.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
        exit()
    #Check if zipped file already exist and ask the user if he want to remove it
    if fileExist(arguments[sizeOfCommand-1]+".zip"):
        answer = ""
        while answer != "yes" and answer != "no":
            answer = input("The file you put as output file already exist do you want to overwrite it ?(yes/no)")
        if answer == "yes":
            os.remove(arguments[sizeOfCommand-1]+".zip")
        else:
            print("If you don't want to delete the existing file please enter a different name")
            exit()
    #We'll need the name to create a temporary directory so we check if it exist first
    if os.path.isdir(arguments[sizeOfCommand-1]):
            print("Please enter another name for the output file")
    #Verify if the file(s) in input exists
    for i in range(5,sizeOfCommand-2):
        if not fileExist(arguments[i]):
            print("The files you enter to cipher or decipher must exists.\nThe Command as to be like this: filecrypt –enc|-dec –key F...F(128bits) –in <input file(s)> -out <output file>")
            print("There is at least one error for the "+str(i-4)+"st/nd/th file")
            exit()
        else:
            print("The file exist")
    if arguments[1] == "-enc":
        return True
    else:
        return False


def createZIP(zipfileName,files):
    # Try to Create Directory to zip all the file together
    try:
        os.mkdir(zipfileName, 0o755)
    except OSError:
        print ("Creation of the directory %s failed" % zipfileName)
        exit()
    else:
        print ("Successfully created the directory %s" % zipfileName)

    if len(files[0]) == 2:
        #Iterate in an array of type {[filePath1, bytesofcipheredFile1,iv],...}
        for fileRessources in files:
            #Crate file inside the newly created directory
            with open(zipfileName+"/"+getFileName(fileRessources[0]), 'wb') as fileDeciphered:
                fileDeciphered.write(fileRessources[1])
                fileDeciphered.close()

    elif len(files[0]) == 3:
        dictForJSON = {}
        if fileExist(getDirName(files[0][0])+"/iv.json"):
            with open(getDirName(files[0][0])+"/iv.json",'rb') as jsonFile:
                dictForJSON = jsonFile.loads(jsonFile.read())
                jsonFile.close()

        for fileRessources in files:
            #Create file inside the newly created directory
            with open(zipfileName+"/"+getFileName(fileRessources[0]), 'wb') as fileCiphered:
                fileCiphered.write(fileRessources[1])
                fileCiphered.close()
            dictForJSON[getFileName(fileRessources[0])] = fileRessources[1]

        #Write the new content of IVs in the json file
        with open(zipfileName+"/iv.json", 'wb') as json:
                json.write(json.dumps(dictForJSON))
                json.close()
    # ZIP the directory
    shutil.make_archive(zipfileName, 'zip', zipfileName)
    #Remove the directory
    shutil.rmtree(zipfileName)

    

def getFileName(absolutPath):
    #Allow to get the filename without the absolute path
    absolutPath = absolutPath[::-1]
    fileName = ""
    i = 0
    while absolutPath[i] != "/":
        fileName += absolutPath[i]
        i += 1
    return fileName[::-1]

def getDirName(path):
    path = path[::-1]
    dirName = ""
    i = 0
    while path[i] != "/":
        i += 1
    dirName = path[i:]
    return dirName[::-1]

def main(arguments):
    # checkInputs(arguments) UT needed for check if zip exist and check if directory exist
    # createZIP() is working
    getDirName("/Users/antoine/Dev/CryptoProject/CryptoProject/Crypto_main.py")
    pass


if __name__ == "__main__":
    main(arguments)

