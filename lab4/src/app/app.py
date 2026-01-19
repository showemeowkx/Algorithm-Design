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
        self.PAGE_LIMIT = 100

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

    def get_records(self, page):
            self.logger.info(f"--- GETTING RECORDS (PAGE {page + 1}) ---")

            try:
                all_indices = self.storage.get_all_records()
                all_indices.sort(key=lambda x: x[0])

                total_records = len(all_indices)
                total_pages = (total_records + self.PAGE_LIMIT - 1) // self.PAGE_LIMIT
                
                if total_pages == 0: total_pages = 1
                if page >= total_pages: page = total_pages - 1
                if page < 0: page = 0

                start = page * self.PAGE_LIMIT
                end = start + self.PAGE_LIMIT
                
                page_indices = all_indices[start : end]
                records = []

                for key, _ in page_indices:
                    rec = self.storage.search(key)
                    if rec:
                        records.append(rec)

                self.logger.info(f"--- RECORDS RECEIVED SUCCSESSFULLY (PAGE {page+1}/{total_pages}) ---")

                return records, total_pages
            except Exception as e:
                self.logger.error(f"An error occurred while fetching records: {e}")
                return [], 1

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
        
        
        