import os
import argparse

DefaultPath = ''
Postfix = ''
BytesDatSig = b'\x05\x00\x00\x00\x0A\x55\xDC\xA2' # Version and valid flag

dirpath = ''
filenameList = []
content = []

def pack():
    indexSection = bytearray(8)  # Count and offset
    global content
    content = [BytesDatSig, indexSection]
    offset = 0
    for i, filename in enumerate(filenameList):
        filepath = os.path.join(dirpath, filename + Postfix)
        with open(filepath, 'rb') as fileOld:
            data = fileOld.read()
        # Append content
        dataHeader = bytearray(filename.encode('cp932'))  # Subfile name
        padLen = 0x20 - len(dataHeader)
        if padLen > 0:
            dataHeader += bytearray(padLen)
        else:
            print('Filename too long', filename)
            return
        dataHeader += int.to_bytes(len(data), 4, byteorder='little')  # Subfile length
        content.append(dataHeader + data)
        # Add index
        indexSection.extend(int.to_bytes(offset, 4, byteorder='little'))
        offset += len(content[-1])
    # Complete index
    indexSection[0:4] = int.to_bytes(len(filenameList), 4, byteorder='little')
    indexSection[4:8] = int.to_bytes(len(BytesDatSig) + len(indexSection), 4, byteorder='little')
    write()

def write():
    path = os.getcwd()  # Get current working directory
    name = 'script.dat'
    filepath = os.path.join(path, name)
    with open(filepath, 'wb') as fileNew:
        for item in content:
            if isinstance(item, (bytes, bytearray)):
                fileNew.write(item)
            else:
                fileNew.write(item.encode('utf-8'))  # Assuming item is a string and encoding it to bytes
    print(f'Write done: {name}')

def main():
    parser = argparse.ArgumentParser(description='Create archive from files in a directory')
    parser.add_argument('directory', metavar='DIR', type=str, help='Directory containing files to archive')
    args = parser.parse_args()

    global dirpath
    global filenameList
    dirpath = args.directory

    if os.path.isdir(dirpath):
        for name in os.listdir(dirpath):
            filename = name.replace(Postfix, '')
            filepath = os.path.join(dirpath, filename + Postfix)
            if os.path.isfile(filepath):
                filenameList.append(filename)
        pack()

if __name__ == "__main__":
    main()
