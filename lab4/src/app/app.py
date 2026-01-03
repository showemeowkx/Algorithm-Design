from utils.logger import Logger
from app.initializer import Initializer

class App:
    def __init__(self, data_dir_path):
        self.data_dir = data_dir_path
        self.initializer = Initializer(self.data_dir)
        self.logger = Logger("App")

    def start(self):
        self.logger.info("--- BEGINNING WORKSPACE INITIALIZATION ---")

        try:
            self.initializer.init_workspace()
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)

        self.logger.info("--- WORKSPACE INITIALIZATIZED SUCCESSFULLY ---")
        
        
        