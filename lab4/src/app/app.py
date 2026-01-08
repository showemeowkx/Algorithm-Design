from utils.logger import Logger
from app.initializer import Initializer
from storage.manager import StorageManager

class App:
    def __init__(self, data_dir_path):
        self.data_dir = data_dir_path
        self.initializer = Initializer(self.data_dir)
        self.storage = StorageManager(self.data_dir)
        self.logger = Logger("App")

    def start(self):
        self.logger.info("--- BEGINNING WORKSPACE INITIALIZATION ---")

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
            self.logger.info("--- RECORD FOUND SUCCESSFULLY ---")
            return result
        else:
            self.logger.info("--- FAILED TO FIND A RECORD ---")
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
        
        
        