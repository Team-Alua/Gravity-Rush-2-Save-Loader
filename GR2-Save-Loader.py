import struct
import json
from collections import OrderedDict

file_path = "data0000.bin"
show_offset = True
show_hash = False
loaded_data = 0

def unpack(upstream_data_set):
    global loaded_data
    loaded_data = loaded_data + 1
    currentCursor = file.tell()
    print(hex(file.tell()))
    file.seek(int.from_bytes(file.read(4), byteorder='little'), 0)
    variable_name = file.read(200).split(b'\x00')[0].decode('UTF8') #Use UTF8 because some strings are in Japanese
    print(hex(file.tell()))
    print(variable_name)
    file.seek(currentCursor + 4, 0)
    type = int.from_bytes(file.read(4), byteorder='little')
    data_location = file.tell()
    if type == 0x08:  # List
        list_length = int.from_bytes(file.read(4), byteorder='little')
        name_hash = file.read(4).hex()
        data_location = file.tell()
        value = {}
        for i in range(0, list_length):
            unpack(value)
        value = OrderedDict(sorted(value.items()))
    else:
        if type % 0x10 == 0x0b:  # String
            string_length = int.from_bytes(file.read(4), byteorder='little') - 1
            data_location = type // 0x10
            file.seek(data_location, 0)
            value = file.read(string_length).decode('UTF8')
            file.seek(currentCursor + 0x0c, 0)
        elif type == 0x09:  # Float
            value = struct.unpack('f', file.read(4))[0]
        elif type == 0x0C:  # Boolean
            value = int.from_bytes(file.read(4), byteorder='little') > 0
        else:
            value = file.read(4).hex()
            print("Warring!!! Unknow type!!! %s at %s with value %s" % (hex(type), hex(file.tell()-8), value))
            print()

        name_hash = file.read(4).hex()

    if variable_name == None:
        variable_name = hex(data_location)
    else:
        if show_hash:
            variable_name = variable_name = "%s %s" % (variable_name, name_hash)
        if show_offset:
            variable_name = variable_name = "%s %s" % (variable_name, hex(data_location))
    print(value)
    upstream_data_set[variable_name] = value


file = open(file_path, mode='rb')
data = file.read()

data_set = OrderedDict()
if len(data) > 0x40 and data[0:4] == b'ggdL':
    file.seek(0x0c, 0)
    numOfData = int.from_bytes(file.read(4), byteorder='little')
    while loaded_data < numOfData:
        unpack(data_set)
    print()
    print(data_set)
    print()
    print("Complete with %i/%i data" % (loaded_data, numOfData))
    with open(r"%s.txt" % (file_path.split('.')[0]), 'w', encoding='utf-8') as json_file:
        json.dump(data_set, json_file, indent=4, ensure_ascii=False)
else:
    print("File Incorrect")