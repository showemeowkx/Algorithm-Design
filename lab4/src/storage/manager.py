import os
from utils.logger import Logger

class StorageManager:
    RECORD_SIZE = 64
    INDEX_RECORD_SIZE = 16
    BLOCK_CAPACITY = 100
    MAIN_INDEX_CAPACITY = 1000

    def __init__(self, data_dir_path):
        self.data_dir = data_dir_path
        
        self.data_path = os.path.join(self.data_dir, "data.dat")
        self.index_path = os.path.join(self.data_dir, "index.dat")
        self.overflow_path = os.path.join(self.data_dir, "overflow.dat")

        self.logger = Logger("Storage Manager")

    def add_record(self, data, key=-1):
        if os.path.exists(self.data_path):
            file_size = os.path.getsize(self.data_path)
            record_number = file_size // (self.RECORD_SIZE + 1)
        else:
            record_number = 0

        new_index = record_number + 1 if key == -1 else key
        formatted_data = data.ljust(self.RECORD_SIZE)[:self.RECORD_SIZE] + "\n"

        with open(self.data_path, "a") as f:
            f.write(formatted_data)

        self._write_index(new_index, record_number)

        return new_index
    
    def _write_index(self, new_idnex, record_number):
        indices = []

        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                for line in f.readlines():
                    if line.strip():
                        pair = line.strip().split(',')
                        k, v = pair
                        indices.append((int(k), int(v)))

        if len(indices) < self.MAIN_INDEX_CAPACITY:
            insert_pos = 0

            while insert_pos < len(indices) and indices[insert_pos][0] < new_idnex:
                insert_pos += 1

            indices.insert(insert_pos, (new_idnex, record_number))

            with open(self.index_path, "w") as f:
                for k, v in indices:
                    index_data = f"{k},{v}"
                    formatted_index_data = index_data.ljust(self.INDEX_RECORD_SIZE)[:self.INDEX_RECORD_SIZE] + "\n"
                    f.write(formatted_index_data)

        else:
            with open(self.overflow_path, "a") as f:
                f.write(f"{new_idnex},{record_number}\n")
