from utils.logger import Logger
from app.initializer import Initializer
from storage.manager import StorageManager

class App:
    def __init__(self, data_dir_path, record_size, index_record_size, main_index_capacity, block_capacity):
        self.data_dir = data_dir_path

        self.initializer = Initializer(self.data_dir, index_record_size, block_capacity, main_index_capacity)
        self.storage = StorageManager(self.data_dir, record_size, index_record_size, main_index_capacity, block_capacity)
        self.logger = Logger("App")

        self.BLOCK_CAPACITY = block_capacity
        self.MAIN_INDEX_CAPACITY = main_index_capacity

    def start(self):
        self.logger.info("--- BEGINNING WORKSPACE INITIALIZATION ---")

        if self.BLOCK_CAPACITY > self.MAIN_INDEX_CAPACITY:
            self.logger.error_and_exit("Block capacity can't be larger than main index capacity", 1)

        if self.MAIN_INDEX_CAPACITY % self.BLOCK_CAPACITY != 0:
            self.logger.error_and_exit("Block capacity and main index capacity values must be multiples", 1)

        try:
            self.initializer.init_workspace()
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        self.logger.info("--- WORKSPACE INITIALIZATIZED SUCCESSFULLY ---")

    def get_all(self):
        self.logger.info("--- GETTING ALL RECORDS ---")

        try:
            all_records = []

            indices_main = self.storage._get_indices(area="main")
            indices_overflow = self.storage._get_indices(area="overflow")

            for key, _ in indices_main + indices_overflow:
                result = self.storage.search(key)
                if result: all_records.append(result)
                
            self.logger.info("--- RECORDS RECEIVED SUCESSFULLY ---")

            return all_records
        except Exception as e:
            self.logger.error(f"An error occurred while fetching all records: {e}")
            return []
        
    def get_block(self, block_number):
        self.logger.info(f"--- GETTING RECORDS (BLOCK {block_number+1}) ---")

        try:
            records = []

            block_indices = self.storage._get_index_block(block_number)
            
            for key, _ in block_indices:
                result = self.storage.search(key)
                if result: records.append(result)
                
            self.logger.info("--- RECORDS RECEIVED SUCESSFULLY ---")

            total_blocks = self.storage._get_blocks_count()
            return records, total_blocks
        except Exception as e:
            self.logger.error(f"An error occurred while fetching records (block {block_number+1}): {e}")
            return [], 0
        
    def find_block_number(self, key):
        try:
            indices_main = self.storage._get_indices(area="main")
            indices_overflow = self.storage._get_indices(area="overflow")
            all_indices = indices_main + indices_overflow
            
            for i, (k, _) in enumerate(all_indices):
                if k == key:
                    return i // self.BLOCK_CAPACITY
            return -1
        except Exception as e:
            self.logger.error(f"Error finding block index: {e}")
            return -1

    def add(self, data, key=-1):
        self.logger.info("--- ADDING A NEW RECORD ---")

        try:
            new_id = self.storage.add_record(data, key)
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        if new_id != -1:
            self.logger.info("--- RECORD ADDED SUCCESSFULLY ---")
            return new_id
        else:
            self.logger.info("--- FAILED TO ADD A RECORD ---")
            return -1

    def search(self, key):
        self.logger.info("--- SEARCHING FOR A RECORD ---")

        try:
            result = self.storage.search(key)
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        if result is not None:
            self.logger.info(f"--- RECORD FOUND SUCCESSFULLY (comparisons: {result['comparisons']}) ---")
            return result
        else:
            self.logger.info(f"--- FAILED TO FIND A RECORD ---")
            return -1
        
    def update(self, key, new_value):
        self.logger.info("--- UPDATING A RECORD ---")

        try:
            updated = self.storage.update_record(key, new_value)
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        if updated is not None:
            self.logger.info("--- RECORD UPDATED SUCCESSFULLY ---")
            return updated
        else:
            self.logger.info("--- FAILED TO UPDATE A RECORD ---")
            return -1
        
    def remove(self, key):
        self.logger.info("--- REMOVING A RECORD ---")

        try:
            updated = self.storage.delete_record(key)
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        if updated is not None:
            self.logger.info("--- RECORD REMOVED SUCCESSFULLY ---")
            return updated
        else:
            self.logger.info("--- FAILED TO REMOVE A RECORD ---")
            return -1
        
        
        