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

        if not self._index_exists(new_index, area='main') and not self._index_exists(new_index, area='overflow'):
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
        
    def search(self, key):
        self.logger.info(f"Beginning searching process... (key: {key})")
        indices = self._get_indices()
        output_data = None

        if len(indices) == 0:
            raise Exception("Index file is empty!")

        min_index_main = indices[0][0]
        max_index_main = indices[len(indices)-1][0]

        if min_index_main <= key <= max_index_main:
            self.logger.info("Searching in the main area...")
            output_data = self._search_main(key, indices)

            if output_data is None:
                self.logger.info("Failed to find in the main area")
            
        if output_data is None:
            self.logger.info("Searching in the overflow area...")
            indices = self._get_indices(area='overflow')

            if len(indices) == 0:
                self.logger.warning("Overflow file is empty!")
            else:
                output_data = self._overflow_search(key, indices)

        if output_data is None:
            self.logger.warning(f"Failed to find a record! (key: {key})")
            return None
        else:
            if os.path.exists(self.data_path):
                record_number = output_data[1]
                with open (self.data_path, "r") as f:
                    for line_no, line in enumerate(f):
                        if line_no == record_number:
                            self.logger.info(f"Record found successfully! ({output_data})")
                            return {"key": key, "number": record_number, "value": line.strip()}
                        
            else: raise Exception("Data file doesn't exist!")

    def update_record(self, key, new_value):
        self.logger.info(f"Beginning data changing process... (key: {key})")
        record_to_change = self.search(key)

        if record_to_change is None:
            return None
        
        new_data = record_to_change
        new_data["value"] = new_value
        
        formatted_value = new_value.ljust(self.RECORD_SIZE)[:self.RECORD_SIZE] + "\n"
        file_data = []

        with open (self.data_path, "r") as f:
            self.logger.info("Reading old file data...")
            file_data = f.readlines()

            if len(file_data) < 0:
                raise Exception("Data file is empty!")
            
            self.logger.info(f"Changing record data... (record_number: {record_to_change['number']})")
            file_data[record_to_change["number"]] = formatted_value

        with open(self.data_path, "w") as f:
            self.logger.info(f"Replacing with updated data... ({new_data})")
            f.writelines(file_data)

        self.logger.info(f"Record updated successfully! (key: {key}, new_value: {new_value})")
        return new_data
    
    def _get_indices(self, area='main'):
        self.logger.info(f"Getting indices... (area: {area})")
        indices = []
        path = self.overflow_path if area == 'overflow' else self.index_path

        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f.readlines():
                    if line.strip():
                        pair = line.strip().split(',')
                        k, v = pair
                        indices.append((int(k), int(v)))

        return indices
    
    def _index_exists(self, index, area='main'):
        self.logger.info("Checking if index exists... (area: {area})")

        indices = self._get_indices(area)
        keys = []
        result = False

        for k, v in indices:
            keys.append(k)

        if int(index) in keys: result = True

        return result
    
    def _search_main(self, key, indices):
        keys = []

        for k, v in indices:
            keys.append((k))
        
        pos = self._interpolation_search(keys=keys, target_key=key)
        
        if pos != -1: return indices[pos]
        else: return None

    def _overflow_search(self, key, indices):
        for record in indices:
            if record[0] == key:
                return record

        return None

    def _interpolation_search(self, keys, target_key):
        self.logger.info("Using interpolation search...")
        low = 0
        high = len(keys) - 1

        while low <= high and keys[low] <= target_key <= keys[high]:
            if high == low:
                if keys[low] == target_key: return low
                break

            pos =  low + ((target_key-keys[low]) * (high-low))//(keys[high]-keys[low])

            if keys[pos] == target_key:
                return pos
            
            if keys[pos] < target_key:
                low = pos + 1
            else:
                high = pos - 1

        return -1
    
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
