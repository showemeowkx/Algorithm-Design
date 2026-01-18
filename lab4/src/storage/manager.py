import os
from utils.logger import Logger

class StorageManager:
    def __init__(self, data_dir_path, record_size, index_record_size, main_index_capacity, block_capacity):
        self.data_dir = data_dir_path
        self.RECORD_SIZE = record_size
        self.INDEX_RECORD_SIZE = index_record_size
        self.BLOCK_CAPACITY = block_capacity
        self.MAIN_INDEX_CAPACITY = main_index_capacity

        self.BLOCK_SIZE_BYTES = (self.INDEX_RECORD_SIZE + 1) * self.BLOCK_CAPACITY
        self.BLOCKS_COUNT = self.MAIN_INDEX_CAPACITY // self.BLOCK_CAPACITY
        
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

        self.logger.info(f"Calculated record number: {record_number}")\
        
        new_index = key if key != -1 else self._define_auto_key()

        self.logger.info(f"New index for data: {new_index}")

        if not self._index_exists(new_index, area='main') and not self._index_exists(new_index, area='overflow'):
            formatted_data = (data.ljust(self.RECORD_SIZE)[:self.RECORD_SIZE] + "\n").encode('ascii')

            self.logger.info("Writing data...")
            with open(self.data_path, "ab") as f:
                f.write(formatted_data)

            self.logger.info(f"Record data written successfully! ({data})")

            self._write_index(new_index, record_number)

            return new_index
        else:
            self.logger.warning(f"An element with index {new_index} already exists!")
            return -1
        
    def _define_auto_key(self):
        self.logger.info("Defining auto key...")
        
        candidate_key = 1
        current_block_idx = 0
        
        while True:
            if candidate_key > self.MAIN_INDEX_CAPACITY:
                break
                
            indices = self._get_index_block(current_block_idx)
            
            existing_keys_in_block = [k for k, v in indices]
            
            start_key_for_block = (current_block_idx * self.BLOCK_CAPACITY) + 1
            end_key_for_block = start_key_for_block + self.BLOCK_CAPACITY - 1
            
            for k in range(start_key_for_block, end_key_for_block + 1):
                if k not in existing_keys_in_block:
                    if not self._index_exists(k, area='overflow'):
                        return k
            
            current_block_idx += 1
            candidate_key = (current_block_idx * self.BLOCK_CAPACITY) + 1


        candidate_key = self.MAIN_INDEX_CAPACITY + 1
        while self._index_exists(candidate_key, area='overflow'):
             candidate_key += 1
             
        return candidate_key
        
    def search(self, key):
        self.logger.info(f"Beginning searching process... (key: {key})")
        indices = []
        index_pos = None
        area = None
        output_data = None
        c = 0

        block_index = (key - 1) // self.BLOCK_CAPACITY if key <= self.MAIN_INDEX_CAPACITY else self.BLOCKS_COUNT-1
        indices = self._get_index_block(block_index)

        if len(indices) == 0:
            raise Exception("Index file is empty!")

        min_index_main = indices[0][0]
        max_index_main = indices[len(indices)-1][0]

        c += 1
        if min_index_main <= key <= max_index_main:
            self.logger.info("Searching in the main area...")
            output_data, index_pos, c_main = self._search_main(key, indices)
            c += c_main

            if output_data is None: self.logger.info("Failed to find in the main area")
            else: area = "main"
            
        if output_data is None:
            self.logger.info("Searching in the overflow area...")
            indices = self._get_overflow_indices()

            if len(indices) == 0:
                self.logger.warning("Overflow file is empty!")
            else:
                output_data, index_pos, c_overflow = self._overflow_search(key, indices)
                c += c_overflow

                if output_data is not None:
                    area = "overflow"

        if output_data is None:
            self.logger.warning(f"Failed to find a record! (key: {key})")
            return None
        else:
            if os.path.exists(self.data_path):
                record_number = output_data[1]
                with open (self.data_path, "rb") as f:
                    for line_no, line in enumerate(f):
                        if line_no == record_number:
                            self.logger.info(f"Record found successfully! ({output_data})")
                            return {"key": key,
                                    "number": record_number,
                                    "value": line.decode('ascii').strip(),
                                    "area": f"{area} [{block_index}]" if area == 'main' else area,
                                    "index_pos": index_pos,
                                    "comparisons": c}
                        
            else: raise Exception("Data file doesn't exist!")

    def get_all_records(self):
        self.logger.info(f"Getting all records...")

        all_indices = []

        file_size = os.path.getsize(self.index_path)
        total_blocks = file_size // self.BLOCK_SIZE_BYTES
        
        for i in range(total_blocks):
            block = self._get_index_block(i)
            all_indices.extend(block)

        overflow_indices = self._get_overflow_indices()
        all_indices.extend(overflow_indices)

        return all_indices

    def update_record(self, key, new_value):
        self.logger.info(f"Beginning data changing process... (key: {key})")
        record_to_change = self.search(key)

        if record_to_change is None:
            return None
        
        new_data = record_to_change
        new_data["value"] = new_value
        
        formatted_value = (new_value.ljust(self.RECORD_SIZE)[:self.RECORD_SIZE] + "\n").encode('ascii')
        file_data = []

        with open (self.data_path, "rb") as f:
            self.logger.info(f"Reading old file data... (area: {record_to_change['area']})")
            file_data = f.readlines()

            if len(file_data) < 0:
                raise Exception("Data file is empty!")
            
            self.logger.info(f"Changing record data... (record_number: {record_to_change['number']})")
            file_data[record_to_change["number"]] = formatted_value

        with open(self.data_path, "wb") as f:
            self.logger.info(f"Replacing with updated data... ({new_data})")
            f.writelines(file_data)

        self.logger.info(f"Record updated successfully! (key: {key}, new_value: {new_value})")
        return new_data
    
    def delete_record(self, key):
        self.logger.info(f"Beginning data deleting process... (key: {key})")
        record_to_delete = self.search(key)

        if record_to_delete is None:
            return None

        self.logger.info("Deleting a record from data file...")
        self._delete_from_file(self.data_path, record_to_delete["number"])

        self.logger.info(f"Deleting a record from index file... (area: {record_to_delete['area']})")
        index_path = self.index_path if record_to_delete["area"] == "main" else self.overflow_path
        self._delete_from_file(index_path, record_to_delete["index_pos"])

        return record_to_delete
    
    def _get_index_block(self, block_index):
        self.logger.info(f"Getting indices... (block_index: {block_index})")
        indices = []

        if not os.path.exists(self.index_path):
            return indices
        
        with open(self.index_path, "rb") as f:
            offset = block_index * self.BLOCK_SIZE_BYTES
            f.seek(offset)
            block_data = f.read(self.BLOCK_SIZE_BYTES)

            for i in range(0, len(block_data), self.INDEX_RECORD_SIZE+1):
                chunk = block_data[i : i + self.INDEX_RECORD_SIZE+1]
                record = self._parse_index_chunk(chunk)

                if record: indices.append(record)

        return indices
    
    def _get_overflow_indices(self):
        self.logger.info(f"Getting indices from overflow area...")
        indices = []

        if os.path.exists(self.overflow_path):
            with open(self.overflow_path, "rb") as f:
                for line in f.readlines():
                    record = self._parse_index_chunk(line)
                    if record: indices.append(record)

        return indices

    def _get_block_bounds(self, block_index):
        with open (self.index_path, "rb") as f:
            start_offset = block_index * self.BLOCK_SIZE_BYTES
            f.seek(start_offset)

            block_data = f.read(self.BLOCK_SIZE_BYTES)

            if not block_data:
                return None, None
            
            first_chunk = block_data[:self.INDEX_RECORD_SIZE+1]
            first_record = self._parse_index_chunk(first_chunk)

            count = len(block_data) // (self.INDEX_RECORD_SIZE+1)
            if count == 0: return None, None

            end_offset = (count-1) * (self.INDEX_RECORD_SIZE+1)

            last_chunk = block_data[end_offset: end_offset+self.INDEX_RECORD_SIZE+1]
            last_record = self._parse_index_chunk(last_chunk)

            if first_record and last_record:
                return first_record[0], last_record[0]
            
            return None, None
    
    def _parse_index_chunk(self, chunk):
        try:
            line = chunk.decode('ascii').strip()
            if not line: return None
            k, v = line.split(',')
            return int(k), int(v)
        except:
            return None

    def _index_exists(self, index, area='main'):
        self.logger.info(f"Checking if index exists... (area: {area})")

        indices = self._get_index_block(index // self.BLOCK_CAPACITY) if area == 'main' else self._get_overflow_indices()
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
        
        pos, c_main = self._interpolation_search(keys=keys, target_key=key)
        
        if pos != -1: return indices[pos], pos, c_main
        else: return None, None, c_main

    def _overflow_search(self, key, indices):
        c = 0
        for record in indices:
            c += 1
            if record[0] == key:
                return record, indices.index(record), c

        return None, None, c

    def _interpolation_search(self, keys, target_key):
        self.logger.info("Using interpolation search...")
        low = 0
        high = len(keys) - 1
        c = 0

        while low <= high and keys[low] <= target_key <= keys[high]:
            c += 1
            if high == low:
                c += 1
                if keys[low] == target_key: return low, c
                break

            pos =  low + ((target_key-keys[low]) * (high-low))//(keys[high]-keys[low])

            c += 1
            if keys[pos] == target_key:
                return pos, c
            
            if keys[pos] < target_key:
                low = pos + 1
            else:
                high = pos - 1

        return -1, c
    
    def _write_index(self, new_idnex, record_number):
        self.logger.info(f"Beginning index writing process... ({new_idnex},{record_number})")
        
        if new_idnex > self.MAIN_INDEX_CAPACITY:
            block_index = (self.BLOCKS_COUNT) - 1
        else:
            block_index = (new_idnex - 1) // self.BLOCK_CAPACITY

        indices = self._get_index_block(block_index)

        self.logger.info("Defining storage area...")
        if len(indices) < self.BLOCK_CAPACITY:
            self.logger.info("Main area is free. Defining position...")
            insert_pos = 0

            while insert_pos < len(indices) and indices[insert_pos][0] < new_idnex:
                insert_pos += 1

            self.logger.info(f"Position found. Inserting at [{insert_pos}]...")
            indices.insert(insert_pos, (new_idnex, record_number))

            self.logger.info("Rewriting index file...")
            with open(self.index_path, "r+b") as f:
                offset = block_index * self.BLOCK_SIZE_BYTES

                f.seek(offset)

                for k, v in indices:
                    index_data = f"{k},{v}"
                    formatted_index_data = (index_data.ljust(self.INDEX_RECORD_SIZE)[:self.INDEX_RECORD_SIZE] + "\n").encode('ascii')
                    f.write(formatted_index_data)

                empty_slots = self.BLOCK_CAPACITY - len(indices)
                empty_record = ((" " * self.INDEX_RECORD_SIZE) + "\n").encode('ascii')
            
                for _ in range(empty_slots):
                    f.write(empty_record)
        else:
            self.logger.info("Main area is full. Writing into overflow...")
            with open(self.overflow_path, "a") as f:
                f.write(f"{new_idnex},{record_number}\n")

        self.logger.info(f"Index data written successfully! ({new_idnex},{record_number})")

    def _read_block(self, block_index):
        offset = block_index * self.BLOCK_SIZE_BYTES

        with open (self.index_path, "rb") as f:
            f.seek(offset)
            block_data = f.read(self.BLOCK_SIZE_BYTES)

        return block_data

    def _delete_from_file(self, file_path, record_index):
        with open (file_path, "rb") as f:
            self.logger.info("Reading old file data...")
            file_data = f.readlines()

            if len(file_data) < 0:
                raise Exception("File is empty!")
            
            self.logger.info(f"Removing a record... (record_number: {record_index})")
            file_data.pop(record_index)

        with open(file_path, "wb") as f:
            self.logger.info(f"Replacing with updated data...")
            f.writelines(file_data)