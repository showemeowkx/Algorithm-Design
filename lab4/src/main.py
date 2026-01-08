import os
from app.app import App
from ui.main_window import MainWindow

DATA_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')

app = App(data_dir_path=DATA_DIR_PATH)
app.start()

root = MainWindow(app)
root.mainloop()