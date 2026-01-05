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

        self.logger = Logger("StorageManager")

    def add_record(self, data, key=-1):
        self.logger.info(f"Beginning record writing process... (data: {data})")

        if os.path.exists(self.data_path):
            file_size = os.path.getsize(self.data_path)
            record_number = file_size // (self.RECORD_SIZE + 1)
        else:
            record_number = 0

        self.logger.info(f"Calculated record number: {record_number}")

        new_index = record_number + 1 if key == -1 else key

        if key == -1:
            while self._index_exists(new_index):
                self.logger.info("Index exists. Adjusting auto-generated value...")
                new_index += 1

        self.logger.info(f"New index for data: {new_index}")

        if not self._index_exists(new_index):
            formatted_data = data.ljust(self.RECORD_SIZE)[:self.RECORD_SIZE] + "\n"

            self.logger.info("Writing data...")
            with open(self.data_path, "a") as f:
                f.write(formatted_data)

            self.logger.info(f"Record data written successfully! ({data})")

            self._write_index(new_index, record_number)

            return new_index
        else:
            self.logger.warning(f"An element with index {new_index} already exists!")
            return -1
    
    def _get_indices(self):
        self.logger.info("Getting indeces...")
        indices = []

        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                for line in f.readlines():
                    if line.strip():
                        pair = line.strip().split(',')
                        k, v = pair
                        indices.append((int(k), int(v)))

        return indices
    
    def _index_exists(self, index):
        self.logger.info("Checking if index exists...")

        indices = self._get_indices()
        keys = []
        result = False

        for k, v in indices:
            keys.append(k)

        if int(index) in keys: result = True

        return result
    
    def _write_index(self, new_idnex, record_number):
        self.logger.info(f"Beginning index writing process... ({new_idnex},{record_number})")
        indices = self._get_indices()

        self.logger.info("Defining storage area...")
        if len(indices) < self.MAIN_INDEX_CAPACITY:
            self.logger.info("Main area is free. Defining position...")
            insert_pos = 0

            while insert_pos < len(indices) and indices[insert_pos][0] < new_idnex:
                insert_pos += 1

            self.logger.info(f"Position found. Inserting at [{insert_pos}]...")
            indices.insert(insert_pos, (new_idnex, record_number))

            self.logger.info("Rewriting index file...")
            with open(self.index_path, "w") as f:
                for k, v in indices:
                    index_data = f"{k},{v}"
                    formatted_index_data = index_data.ljust(self.INDEX_RECORD_SIZE)[:self.INDEX_RECORD_SIZE] + "\n"
                    f.write(formatted_index_data)
        else:
            self.logger.info("Main area is full. Writing into overflow...")
            with open(self.overflow_path, "a") as f:
                f.write(f"{new_idnex},{record_number}\n")

        self.logger.info(f"Index data written successfully! ({new_idnex},{record_number})")
