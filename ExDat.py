import os
import struct
from argparse import ArgumentParser

def is_sane_count(count):
    # Example sanity check, adjust as needed
    return count > 0 and count < 400000

def extract_dat(file_path, output_dir):
    print(f"Extracting '{file_path}' to '{output_dir}'")

    with open(file_path, 'rb') as file:
        file_data = file.read()

        count = struct.unpack('I', file_data[8:12])[0]
        if not is_sane_count(count):
            print(f"Invalid count: {count}")
            return

        print(f"File count: {count}")

        base_offset = struct.unpack('I', file_data[0x0c:0x10])[0]
        index_offset = 0x10
        index_size = 4 * count
        if base_offset >= len(file_data) or base_offset < (index_offset + index_size):
            print("Invalid offsets")
            return

        index = []
        for i in range(count):
            offset = struct.unpack('I', file_data[index_offset:index_offset + 4])[0]
            if offset != 0xffffffff:
                index.append(base_offset + offset)
            index_offset += 4

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        index.sort()

        for i, offset in enumerate(index):
            name_offset = offset
            name_end = file_data.find(b'\x00', name_offset)
            name = file_data[name_offset:name_end].decode('cp932')
            if not name:
                name = f"{i:02d}_{base_name}#{i:02d}"
                if file_data[name_end + 1:name_end + 5] == b'_BMD':
                    name += ".bmd"

            next_offset = len(file_data) if i == len(index) - 1 else index[i + 1]
            file_size = next_offset - (offset + 0x24)
            file_data_offset = offset + 0x24

            file_path = os.path.join(output_dir, name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            print(f"Extracting '{name}' ({file_size} bytes)")
            with open(file_path, 'wb') as out_file:
                out_file.write(file_data[file_data_offset:file_data_offset + file_size])

if __name__ == "__main__":
    parser = ArgumentParser(description="Extract files from a BlackRainbow resource archive (.dat or .pak)")
    parser.add_argument("input_file", help="Path to the input archive file")
    parser.add_argument("output_dir", help="Path to the output directory")
    args = parser.parse_args()

    extract_dat(args.input_file, args.output_dir)
