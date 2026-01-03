import logging
import sys

class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def error_and_exit(self, message, status):
        self.error(message)
        self.info(f"Exiting with {status}...")
        sys.exit(status)   