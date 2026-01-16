from generate import generate_data
import time
import shutil
import os

FILES_BASE_PATH = "./files"
CHUNK_SIZE_BYTES = 25 * 1024 * 1024 

def extract_key_from_line(line):
    return int(line.partition(' ')[0])

def format_time(seconds):
    time_output = ""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds_left = seconds % 60

    if hours >= 1:
        time_output += f"{int(hours)} hours, "

    if minutes >= 1:
        time_output += f"{int(minutes)} minutes, "

    time_output += f"{round(seconds_left, 2)} seconds"

    return time_output

def split_into_sorted_chunks(input_file):
    chunk_files = []
    
    chunk_data = []
    curr_size = 0
    chunk_index = 0

    with open(f"{FILES_BASE_PATH}/{input_file}", "r") as file:
        for line in file:
            chunk_data.append(line)
            curr_size += len(line)

            if curr_size >= CHUNK_SIZE_BYTES:
                chunk_data.sort(key=extract_key_from_line)
                
                chunk_filename = f"{FILES_BASE_PATH}/chunk{chunk_index}.txt"

                with open(chunk_filename, "w") as chunk_file:
                    chunk_file.writelines(chunk_data)
                
                chunk_files.append(chunk_filename)
                
                chunk_data = []
                curr_size = 0
                chunk_index += 1

        if chunk_data:
            chunk_data.sort(key=extract_key_from_line)
            chunk_filename = f"{FILES_BASE_PATH}/chunk{chunk_index}.txt"

            with open(chunk_filename, "w") as chunk_f:
                chunk_f.writelines(chunk_data)

            chunk_files.append(chunk_filename)

    return chunk_files

def merge_chunks(chunk_files, output_file):    
    files = []
    current_lines = []

    try:
        for filename in chunk_files:
            f = open(filename, "r")
            line = f.readline()
            if line:
                files.append(f)
                current_lines.append((extract_key_from_line(line), line))
            else:
                f.close()

        with open(f"{FILES_BASE_PATH}/{output_file}", "w") as out_file:
            while current_lines:
                min_index = 0
                min_val = current_lines[0][0]
                
                for i in range(1, len(current_lines)):
                    if current_lines[i][0] < min_val:
                        min_val = current_lines[i][0]
                        min_index = i
                
                _, line_to_write = current_lines[min_index]
                out_file.write(line_to_write)
                
                next_line = files[min_index].readline()
                
                if next_line:
                    current_lines[min_index] = (extract_key_from_line(next_line), next_line)
                else:
                    files[min_index].close()
                    files.pop(min_index)
                    current_lines.pop(min_index)

    finally:
        for f in files:
            f.close()

def sort_adaptive_asc(filename, file_size_mb=1000, max_string_len=20):
    # generate_data(f"{FILES_BASE_PATH}/{filename}", file_size_mb, max_string_len)

    start_time = time.time()
    print(f"STARTING SORTING PROCESS... [{start_time}]")

    chunk_files = split_into_sorted_chunks(filename)
    merge_chunks(chunk_files, filename)

    for f in chunk_files:
        if os.path.exists(f):
            os.remove(f)

    end_time = time.time()

    print(f"SORTING EXECUTED SUCCESSFULLY [{end_time}]")
    print("PROCESSING TIME:", format_time(end_time - start_time))

shutil.copyfile('./data_1GB.txt', './files/data.txt')

sort_adaptive_asc("data.txt", file_size_mb=500)