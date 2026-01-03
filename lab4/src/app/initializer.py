import os
from utils.logger import Logger

class Initializer:
    def __init__(self, data_dir_path):
        self.data_dir = data_dir_path

        self.index_filename = "index.dat"
        self.data_filename = "data.dat"
        self.overflow_filename = "overflow.dat"

        self.index_path = os.path.join(self.data_dir, self.index_filename)
        self.data_path = os.path.join(self.data_dir, self.data_filename)
        self.overflow_path = os.path.join(self.data_dir, self.overflow_filename)

        self.logger = Logger("Initializer")

    def init_workspace(self):
        files_to_check = [self.index_path, self.data_path, self.overflow_path]
        missing_files = []

        self.logger.info("Checking data directory availability...")
        if not os.path.exists(self.data_dir):
            self.logger.info("Data directory not found. Creating from scratch...")

            os.mkdir(self.data_dir)
            self.logger.info("Data directory created successfully")

            self.create_data_files(files_to_check)

        else:
            self.logger.info("Data directory found. Looking for files...")

            for file in files_to_check:
                filename = os.path.basename(file)
                self.logger.info(f"Looking for {filename} file...")

                if os.path.isfile(file):
                    self.logger.info(f"File {filename} found")
                else:
                    self.logger.warning(f"WARNING: File {filename} not found. Marking as missing...")
                    missing_files.append(file)

            if len(missing_files) > 0:
                self.logger.info(f"Creating missing files ({len(missing_files)})...")
                self.create_data_files(missing_files)

        self.logger.info("Workspace initialized successfully!")

    def create_data_files(self, settings):
        try:
            for file in settings:
                with open(file, 'x') as f:
                    self.logger.info(f"File {os.path.basename(file)} created successfully")
        except Exception as e:
            self.logger.error_and_exit(f"An unexpected error occurred: {e}", 1)
        
        