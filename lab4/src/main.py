import os
from app.app import App
from ui.main_window import MainWindow

DATA_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')
RECORD_SIZE = 64
INDEX_RECORD_SIZE = 16
MAIN_INDEX_CAPACITY = 1000
BLOCK_CAPACITY = 100

app = App(data_dir_path=DATA_DIR_PATH,
          record_size=RECORD_SIZE,
          index_record_size=INDEX_RECORD_SIZE,
          main_index_capacity=MAIN_INDEX_CAPACITY,
          block_capacity=BLOCK_CAPACITY)

app.start()

root = MainWindow(app, record_size=RECORD_SIZE, index_record_size=INDEX_RECORD_SIZE)
root.mainloop()