import os
import random
import string
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

def fill_database(count=10000):
    print(f"Generating {count} records...")
    keys = random.sample(range(1, 100000), count)
    
    for i, key in enumerate(keys):
        data = ''.join(random.choices(string.ascii_letters, k=20))
        app.add(data, key)
        if i % 1000 == 0:
            print(f"Progress: {i}/{count}")
    print("Database filled successfully!")

def run_experiment(num_searches=20):
    keys = []

    if os.path.exists(app.storage.index_path):
        file_size = os.path.getsize(app.storage.index_path)
        total_blocks = file_size // app.storage.BLOCK_SIZE_BYTES

        if total_blocks > 0:
            for _ in range(num_searches):
                rand_block_idx = random.randint(0, total_blocks - 1)
                block_data = app.storage._get_index_block(rand_block_idx)
                if block_data:
                    key = random.choice(block_data)[0]
                    keys.append(key)

    if os.path.exists(app.storage.overflow_path):
        overflow_indices = app.storage._get_overflow_indices()
        if overflow_indices:
            overflow_keys = [k for k, _ in overflow_indices]
            count = min(len(overflow_keys), num_searches)
            keys.extend(random.sample(overflow_keys, count))

    random.shuffle(keys)
    test_keys = keys[:num_searches]

    total_comparisons = 0

    print("\n--- RUNNING EFFICIENCY TEST ---")
    for key in test_keys:
        result = app.storage.search(key)
        total_comparisons += result['comparisons']
        print(f"Key: {key:5} | Area: {result['area']:8} | Comparisons: {result['comparisons']}")

    average = total_comparisons / num_searches
    print(f"\nAverage comparisons for {num_searches} searches: {average:.2f}")
    return average

# fill_database(5000)
# run_experiment()

root = MainWindow(app, record_size=RECORD_SIZE, index_record_size=INDEX_RECORD_SIZE)
root.mainloop()