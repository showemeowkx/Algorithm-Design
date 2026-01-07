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
        
        
        